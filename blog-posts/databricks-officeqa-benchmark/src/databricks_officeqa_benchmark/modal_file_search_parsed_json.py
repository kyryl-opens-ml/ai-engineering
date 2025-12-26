import os
import time
import zipfile
from pathlib import Path

import modal


app = modal.App("databricks-officeqa-benchmark-file-search-parsed-json")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-genai>=1.56.0"
)
gemini_secret = modal.Secret.from_name("gemini")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)


def _unzip_json_archives(jsons_dir: Path) -> None:
    if any(jsons_dir.rglob("*.json")):
        return
    for z in sorted(jsons_dir.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(jsons_dir)


@app.function(
    image=image,
    secrets=[gemini_secret],
    timeout=60 * 60 * 8,
    volumes={str(VOLUME_MOUNT): volume},
)
def create_file_search_store_for_parsed_json(
    storage_path: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    max_files: int | None = None,
    poll_interval_s: int = 5,
    log_every: int = 25,
) -> str:
    from google import genai

    root = Path(storage_path)
    if not root.exists():
        raise FileNotFoundError(storage_path)

    jsons_dir = root / "treasury_bulletins_parsed" / "jsons"
    if not jsons_dir.exists():
        raise FileNotFoundError(str(jsons_dir))

    _unzip_json_archives(jsons_dir)
    files = sorted(jsons_dir.rglob("*.json"))
    if max_files is not None:
        files = files[:max_files]
    if not files:
        raise RuntimeError(f"No .json files found in {jsons_dir}")

    client = genai.Client()
    store = client.file_search_stores.create(
        config={
            "display_name": store_display_name
            or f"officeqa-parsed-json-{int(time.time())}"
        }
    )

    total = len(files)
    for i, path in enumerate(files, start=1):
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
        if log_every > 0 and (i % log_every == 0 or i == total):
            print(f"Uploaded {i}/{total}")

    return store.name


@app.local_entrypoint()
def main(
    storage_path: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    max_files: int | None = None,
) -> None:
    store_name = create_file_search_store_for_parsed_json.remote(
        storage_path=storage_path,
        store_display_name=store_display_name,
        max_files=max_files,
    )
    print(store_name)
