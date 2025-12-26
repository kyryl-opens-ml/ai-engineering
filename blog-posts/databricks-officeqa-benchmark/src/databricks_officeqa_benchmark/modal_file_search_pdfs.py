import os
import json
import time
from pathlib import Path

import modal


app = modal.App("databricks-officeqa-benchmark-file-search-pdfs")

image = modal.Image.debian_slim(python_version="3.12").pip_install("google-genai>=1.56.0")
gemini_secret = modal.Secret.from_name("gemini")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)

ROOT_DIR = VOLUME_MOUNT / "officeqa"
REPO_DIR = ROOT_DIR / "repo"
PDF_DIR = REPO_DIR / "treasury_bulletin_pdfs"
MANIFEST_PATH = ROOT_DIR / "manifest.json"
RUNS_DIR = ROOT_DIR / "file_search_runs"


@app.function(
    image=image,
    secrets=[gemini_secret],
    timeout=60 * 60 * 12,
    volumes={str(VOLUME_MOUNT): volume},
)
def create_pdf_file_search_store(
    store_display_name: str | None = None,
    max_files: int | None = None,
    poll_interval_s: int = 5,
    max_file_size_mb: int = 100,
) -> str:
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")
    if not PDF_DIR.exists():
        raise FileNotFoundError(str(PDF_DIR))

    run_id = int(time.time())
    started_at = time.time()

    client = genai.Client(api_key=api_key)
    store = client.file_search_stores.create(
        config={
            "display_name": store_display_name or f"officeqa-pdfs-{run_id}"
        }
    )

    files = sorted(PDF_DIR.rglob("*.pdf"))
    if max_files is not None:
        files = files[: max(0, max_files)]

    max_bytes = max(1, max_file_size_mb) * 1024 * 1024
    uploaded = 0
    skipped_too_large = 0
    for path in files:
        size = path.stat().st_size
        if size > max_bytes:
            print(f"skip_too_large path={path} bytes={size}")
            skipped_too_large += 1
            continue
        display_name = str(path.relative_to(PDF_DIR))
        op = client.file_search_stores.upload_to_file_search_store(
            file=str(path),
            file_search_store_name=store.name,
            config={"display_name": display_name},
        )
        while not op.done:
            time.sleep(poll_interval_s)
            op = client.operations.get(op)
        uploaded += 1

    manifest = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else None
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "run_id": run_id,
        "corpus": "pdfs",
        "store_name": store.name,
        "store_display_name": store_display_name or f"officeqa-pdfs-{run_id}",
        "source_dir": str(PDF_DIR),
        "file_glob": "**/*.pdf",
        "limits": {"max_files": max_files, "max_file_size_mb": max_file_size_mb},
        "counts": {
            "considered": len(files),
            "uploaded": uploaded,
            "skipped_too_large": skipped_too_large,
        },
        "officeqa": {"commit": (manifest or {}).get("commit")} if manifest else None,
        "timing_s": {"started_at": started_at, "finished_at": time.time()},
    }
    (RUNS_DIR / f"pdfs_{run_id}.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    volume.commit()

    return store.name


@app.local_entrypoint()
def main(
    store_display_name: str | None = None,
    max_files: int | None = None,
    poll_interval_s: int = 5,
    max_file_size_mb: int = 100,
) -> None:
    store_name = create_pdf_file_search_store.remote(
        store_display_name=store_display_name,
        max_files=max_files,
        poll_interval_s=poll_interval_s,
        max_file_size_mb=max_file_size_mb,
    )
    print(store_name)
