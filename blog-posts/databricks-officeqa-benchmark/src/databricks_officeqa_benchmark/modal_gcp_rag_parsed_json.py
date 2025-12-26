import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

import modal

app = modal.App("databricks-officeqa-benchmark-gcp-rag-parsed-json")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-genai>=1.56.0"
)
gcp_secret = modal.Secret.from_name("gcp")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)


def _ensure_adc() -> None:
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    sa = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if not sa:
        return
    path = Path("/tmp/gcp_sa.json")
    path.write_text(sa)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)


def _client():
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    if not project:
        raise RuntimeError(
            "Set GOOGLE_CLOUD_PROJECT (or GCP_PROJECT) or GEMINI_API_KEY"
        )

    location = (
        os.environ.get("GCP_LOCATION")
        or os.environ.get("GOOGLE_CLOUD_LOCATION")
        or "us-central1"
    )
    _ensure_adc()
    return genai.Client(vertexai=True, project=project, location=location)


def _walk_elements(obj: dict[str, Any]) -> Iterable[dict[str, Any]]:
    doc = obj.get("document") or {}
    elements = doc.get("elements")
    if not isinstance(elements, list):
        return
    for el in elements:
        if isinstance(el, dict):
            yield el


def _is_table_content(s: str) -> bool:
    return "<table" in s.lower()


def _first_present(el: dict[str, Any], keys: Iterable[str]) -> Any:
    for k in keys:
        v = el.get(k)
        if v is not None:
            return v
    return None


def _extract_page(el: dict[str, Any]) -> int | None:
    v = _first_present(
        el, ("page", "page_num", "page_number", "pageIndex", "page_index", "pageNo")
    )
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if isinstance(v, str) and v.isdigit():
        return int(v)
    return None


def _extract_bbox(el: dict[str, Any]) -> Any:
    return _first_present(
        el,
        (
            "bbox",
            "bounding_box",
            "boundingBox",
            "bounding_poly",
            "boundingPoly",
            "layout",
        ),
    )


def _extract_kind(el: dict[str, Any], content: str) -> str:
    v = _first_present(el, ("type", "kind", "category", "element_type"))
    if isinstance(v, str) and v.strip():
        return v.strip()
    return "table" if _is_table_content(content) else "text"


def _chunks_for_file(
    json_path: Path, *, chunk_chars: int, max_chunks: int | None
) -> Iterable[dict[str, Any]]:
    obj = json.loads(json_path.read_text(encoding="utf-8"))
    chunk_idx = 0
    buf: list[str] = []
    elements_meta: list[dict[str, Any]] = []
    buf_chars = 0

    def flush() -> dict[str, Any] | None:
        nonlocal chunk_idx, buf, elements_meta, buf_chars
        if not buf:
            return None
        pages = [m.get("page") for m in elements_meta if isinstance(m.get("page"), int)]
        meta: dict[str, Any] = {
            "source_file": json_path.name,
            "chunk_index": chunk_idx,
        }
        if pages:
            meta["page_start"] = min(pages)
            meta["page_end"] = max(pages)
        meta["elements"] = elements_meta
        rec = {
            "id": f"{json_path.stem}:{chunk_idx:06d}",
            "text": "\n\n".join(buf).strip(),
            "metadata": meta,
        }
        chunk_idx += 1
        buf = []
        elements_meta = []
        buf_chars = 0
        return rec

    for i, el in enumerate(_walk_elements(obj)):
        content = el.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
        kind = _extract_kind(el, content)
        page = _extract_page(el)
        bbox = _extract_bbox(el)

        el_meta: dict[str, Any] = {"i": i, "kind": kind}
        if page is not None:
            el_meta["page"] = page
        if bbox is not None:
            el_meta["bbox"] = bbox

        projected = buf_chars + len(content) + (2 if buf else 0)
        if buf and projected > chunk_chars:
            rec = flush()
            if rec is not None:
                yield rec
                if max_chunks is not None and chunk_idx >= max_chunks:
                    return

        buf.append(content)
        elements_meta.append(el_meta)
        buf_chars = projected

    rec = flush()
    if rec is not None:
        yield rec


def _maybe_unzip(repo_dir: Path) -> Path:
    tbp = repo_dir / "treasury_bulletins_parsed"
    unzip_py = tbp / "unzip.py"
    jsons_dir = tbp / "jsons"

    has_json = jsons_dir.exists() and any(
        p.suffix == ".json" for p in jsons_dir.glob("*.json")
    )
    if has_json:
        return jsons_dir

    if not unzip_py.exists():
        raise FileNotFoundError(str(unzip_py))

    subprocess.run(["python3", str(unzip_py)], cwd=str(tbp), check=True)
    return jsons_dir


@app.function(
    image=image,
    secrets=[gcp_secret],
    timeout=60 * 60 * 8,
    volumes={str(VOLUME_MOUNT): volume},
)
def upload_parsed_json_to_gcp_rag_corpus(
    *,
    repo_dir: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    max_files: int | None = None,
    chunk_chars: int = 6000,
    max_chunks_per_file: int | None = None,
    poll_interval_s: int = 5,
) -> str:
    repo = Path(repo_dir)
    if not repo.exists():
        raise FileNotFoundError(repo_dir)

    jsons_dir = _maybe_unzip(repo)
    if not jsons_dir.exists():
        raise FileNotFoundError(str(jsons_dir))

    client = _client()
    store = client.file_search_stores.create(
        config={
            "display_name": store_display_name
            or f"officeqa-parsed-json-{int(time.time())}"
        }
    )

    paths = sorted(jsons_dir.glob("treasury_bulletin_*.json"))
    if max_files is not None:
        paths = paths[:max_files]

    out_dir = Path("/tmp/officeqa_parsed_json_jsonl")
    out_dir.mkdir(parents=True, exist_ok=True)

    for src in paths:
        out_path = out_dir / f"{src.stem}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for rec in _chunks_for_file(
                src, chunk_chars=chunk_chars, max_chunks=max_chunks_per_file
            ):
                f.write(json.dumps(rec, ensure_ascii=False))
                f.write("\n")

        op = client.file_search_stores.upload_to_file_search_store(
            file=str(out_path),
            file_search_store_name=store.name,
            config={"display_name": out_path.name},
        )
        while not op.done:
            time.sleep(poll_interval_s)
            op = client.operations.get(op)
        out_path.unlink(missing_ok=True)

    return store.name


@app.local_entrypoint()
def main(
    repo_dir: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    max_files: int | None = None,
    chunk_chars: int = 6000,
    max_chunks_per_file: int | None = None,
) -> None:
    store_name = upload_parsed_json_to_gcp_rag_corpus.remote(
        repo_dir=repo_dir,
        store_display_name=store_display_name,
        max_files=max_files,
        chunk_chars=chunk_chars,
        max_chunks_per_file=max_chunks_per_file,
    )
    print(store_name)
