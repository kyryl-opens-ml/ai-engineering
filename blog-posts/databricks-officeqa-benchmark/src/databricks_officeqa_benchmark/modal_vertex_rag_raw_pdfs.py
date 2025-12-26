import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import modal

app = modal.App("databricks-officeqa-benchmark-vertex-rag-raw-pdfs")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-cloud-aiplatform>=1.113.0",
)

gcp_secret = modal.Secret.from_name("gcp")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)

DEFAULT_PDFS_DIR = VOLUME_MOUNT / "officeqa" / "repo" / "treasury_bulletin_pdfs"
DEFAULT_STATE_PATH = (
    VOLUME_MOUNT / "officeqa" / "gcp_rag" / "raw_pdfs" / "upload_state.json"
)


@dataclass(frozen=True)
class UploadStats:
    attempted: int
    uploaded: int
    skipped: int
    failed: int
    remote_files: int | None


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "version": 1,
            "corpus_name": None,
            "created_at_unix": int(time.time()),
            "updated_at_unix": int(time.time()),
            "files": {},
        }
    return json.loads(path.read_text())


def _ensure_gcp_auth() -> None:
    sa_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        p = Path("/tmp/gcp_sa.json")
        p.write_text(sa_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(p)


def _vertex_rag() -> object:
    import vertexai
    from google.cloud import aiplatform
    from vertexai.preview import rag

    project = os.environ.get("GCP_PROJECT")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    if not project:
        raise RuntimeError("GCP_PROJECT is required")
    aiplatform.init(project=project, location=location)
    vertexai.init(project=project, location=location)
    return rag


def _await_if_operation(obj: object, poll_interval_s: int) -> object:
    if hasattr(obj, "done") and callable(getattr(obj, "done")):
        while not obj.done():
            time.sleep(poll_interval_s)
        if hasattr(obj, "result") and callable(getattr(obj, "result")):
            return obj.result()
    return obj


def _rag_upload_pdf(
    rag: object, *, corpus_name: str, path: Path, display_name: str
) -> object:
    import inspect

    params = set(inspect.signature(rag.upload_file).parameters)
    kwargs = {"path": str(path), "display_name": display_name}
    if "corpus_name" in params:
        return rag.upload_file(corpus_name=corpus_name, **kwargs)
    if "corpus" in params:
        return rag.upload_file(corpus=corpus_name, **kwargs)
    return rag.upload_file(corpus_name, str(path), display_name=display_name)


def _count_remote_files(rag: object, corpus_name: str) -> int | None:
    try:
        import inspect

        params = set(inspect.signature(rag.list_files).parameters)
        if "corpus_name" in params:
            files = rag.list_files(corpus_name=corpus_name)
        elif "corpus" in params:
            files = rag.list_files(corpus=corpus_name)
        else:
            files = rag.list_files(corpus_name)
        return sum(1 for _ in files)
    except Exception:
        return None


@app.function(
    image=image,
    secrets=[gcp_secret],
    timeout=60 * 60 * 12,
    volumes={str(VOLUME_MOUNT): volume},
)
def upload_raw_pdfs_to_vertex_rag_corpus(
    *,
    pdfs_dir: str = str(DEFAULT_PDFS_DIR),
    state_path: str = str(DEFAULT_STATE_PATH),
    corpus_display_name: str | None = None,
    corpus_name: str | None = None,
    max_files: int | None = None,
    poll_interval_s: int = 5,
) -> str:
    _ensure_gcp_auth()
    rag = _vertex_rag()

    root = Path(pdfs_dir)
    if not root.exists():
        raise FileNotFoundError(pdfs_dir)

    state_file = Path(state_path)
    state = _load_state(state_file)

    if corpus_name:
        state["corpus_name"] = corpus_name
    if state.get("corpus_name") is None:
        corpus = rag.create_corpus(
            display_name=corpus_display_name or f"officeqa-raw-pdfs-{int(time.time())}"
        )
        state["corpus_name"] = getattr(corpus, "name", None) or corpus
        state["updated_at_unix"] = int(time.time())
        _atomic_write_json(state_file, state)
        volume.commit()

    corpus_name = state["corpus_name"]
    pdfs = sorted(root.glob("*.pdf"))
    if max_files is not None:
        pdfs = pdfs[:max_files]

    attempted = 0
    uploaded = 0
    skipped = 0
    failed = 0

    for path in pdfs:
        key = path.name
        existing = state["files"].get(key)
        if existing and existing.get("status") == "uploaded":
            skipped += 1
            continue

        attempted += 1
        entry = {
            "file_name": key,
            "local_path": str(path),
            "updated_at_unix": int(time.time()),
            "status": "uploading",
        }
        state["files"][key] = entry
        state["updated_at_unix"] = int(time.time())
        _atomic_write_json(state_file, state)
        volume.commit()

        try:
            result = _rag_upload_pdf(
                rag, corpus_name=corpus_name, path=path, display_name=key
            )
            result = _await_if_operation(result, poll_interval_s=poll_interval_s)
            entry["status"] = "uploaded"
            entry["rag_file_name"] = getattr(result, "name", None) or str(result)
            uploaded += 1
        except Exception as e:
            entry["status"] = "failed"
            entry["error"] = f"{type(e).__name__}: {e}"
            failed += 1
        finally:
            entry["updated_at_unix"] = int(time.time())
            state["updated_at_unix"] = int(time.time())
            _atomic_write_json(state_file, state)
            volume.commit()

    remote_files = _count_remote_files(rag, corpus_name=corpus_name)
    stats = UploadStats(
        attempted=attempted,
        uploaded=uploaded,
        skipped=skipped,
        failed=failed,
        remote_files=remote_files,
    )
    state["last_run"] = {
        "finished_at_unix": int(time.time()),
        "stats": {
            "attempted": stats.attempted,
            "uploaded": stats.uploaded,
            "skipped": stats.skipped,
            "failed": stats.failed,
            "remote_files": stats.remote_files,
        },
    }
    state["updated_at_unix"] = int(time.time())
    _atomic_write_json(state_file, state)
    volume.commit()

    return corpus_name


@app.local_entrypoint()
def main(
    pdfs_dir: str = str(DEFAULT_PDFS_DIR),
    corpus_display_name: str | None = None,
    corpus_name: str | None = None,
    max_files: int | None = None,
    state_path: str = str(DEFAULT_STATE_PATH),
) -> None:
    corpus_id = upload_raw_pdfs_to_vertex_rag_corpus.remote(
        pdfs_dir=pdfs_dir,
        state_path=state_path,
        corpus_display_name=corpus_display_name,
        corpus_name=corpus_name,
        max_files=max_files,
    )
    print(corpus_id)
