import os
import subprocess
import time
from pathlib import Path
from typing import Iterable

import modal

app = modal.App("databricks-officeqa-benchmark-parsed-json-file-search")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-genai>=1.56.0"
)
gemini_secret = modal.Secret.from_name("gemini")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)


def _iter_files(root: Path, include_glob: str) -> Iterable[Path]:
    for path in root.glob(include_glob):
        if path.is_file():
            yield path


def _ensure_unzipped(repo_dir: Path) -> Path:
    tbp = repo_dir / "treasury_bulletins_parsed"
    unzip_py = tbp / "unzip.py"
    jsons_dir = tbp / "jsons"

    if jsons_dir.exists() and any(jsons_dir.glob("*.json")):
        return jsons_dir

    if not unzip_py.exists():
        raise FileNotFoundError(str(unzip_py))

    subprocess.run(["python3", str(unzip_py)], cwd=str(tbp), check=True)
    return jsons_dir


@app.function(
    image=image,
    secrets=[gemini_secret],
    timeout=60 * 60 * 8,
    volumes={str(VOLUME_MOUNT): volume},
)
def create_parsed_json_file_search_store(
    *,
    repo_dir: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    include_glob: str = "treasury_bulletin_*.json",
    max_files: int | None = None,
    poll_interval_s: int = 5,
) -> str:
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")

    repo = Path(repo_dir)
    if not repo.exists():
        raise FileNotFoundError(repo_dir)

    jsons_dir = _ensure_unzipped(repo)
    client = genai.Client(api_key=api_key)
    store = client.file_search_stores.create(
        config={
            "display_name": store_display_name
            or f"officeqa-parsed-json-{int(time.time())}"
        }
    )

    files = list(_iter_files(jsons_dir, include_glob))
    if max_files is not None:
        files = files[:max_files]

    for path in files:
        op = client.file_search_stores.upload_to_file_search_store(
            file=str(path),
            file_search_store_name=store.name,
            config={"display_name": path.name},
        )
        while not op.done:
            time.sleep(poll_interval_s)
            op = client.operations.get(op)

    return store.name


@app.local_entrypoint()
def main(
    repo_dir: str = "/vol/officeqa/repo",
    store_display_name: str | None = None,
    include_glob: str = "treasury_bulletin_*.json",
    max_files: int | None = None,
) -> None:
    store_name = create_parsed_json_file_search_store.remote(
        repo_dir=repo_dir,
        store_display_name=store_display_name,
        include_glob=include_glob,
        max_files=max_files,
    )
    print(store_name)
