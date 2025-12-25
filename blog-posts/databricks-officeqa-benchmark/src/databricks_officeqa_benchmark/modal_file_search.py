import os
import time
from pathlib import Path
from typing import Iterable

import modal


app = modal.App("databricks-officeqa-benchmark-file-search")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-genai>=1.56.0"
)

gemini_secret = modal.Secret.from_name("gemini")


def _iter_files(root: Path, include_glob: str) -> Iterable[Path]:
    for path in root.glob(include_glob):
        if path.is_file():
            yield path


@app.function(image=image, secrets=[gemini_secret], timeout=60 * 60)
def upload_storage_to_file_search_store(
    storage_path: str,
    store_display_name: str | None = None,
    include_glob: str = "**/*",
    max_files: int | None = None,
    poll_interval_s: int = 5,
) -> str:
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")

    root = Path(storage_path)
    if not root.exists():
        raise FileNotFoundError(storage_path)

    client = genai.Client(api_key=api_key)
    store = client.file_search_stores.create(
        config={
            "display_name": store_display_name
            or f"file-search-store-{int(time.time())}"
        }
    )

    files = list(_iter_files(root, include_glob))
    if max_files is not None:
        files = files[:max_files]

    for path in files:
        display_name = (
            str(path.relative_to(root)) if path.is_relative_to(root) else path.name
        )
        op = client.file_search_stores.upload_to_file_search_store(
            file=str(path),
            file_search_store_name=store.name,
            config={"display_name": display_name},
        )
        while not op.done:
            time.sleep(poll_interval_s)
            op = client.operations.get(op)

    return store.name


@app.local_entrypoint()
def main(
    storage_path: str,
    store_display_name: str | None = None,
    include_glob: str = "**/*",
    max_files: int | None = None,
) -> None:
    store_name = upload_storage_to_file_search_store.remote(
        storage_path=storage_path,
        store_display_name=store_display_name,
        include_glob=include_glob,
        max_files=max_files,
    )
    print(store_name)
