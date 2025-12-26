import os
import time
import zipfile
from pathlib import Path

import modal


app = modal.App("databricks-officeqa-benchmark-gcp-rag-transformed-txt")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-cloud-aiplatform>=1.132.0"
)

gcp_secret = modal.Secret.from_name("gcp")

DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)


def _ensure_google_application_credentials() -> None:
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON") or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS_JSON"
    )
    if not raw:
        return
    path = Path("/tmp/gcp-service-account.json")
    path.write_text(raw)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)


def _load_transformed_txt_files(transformed_dir: Path) -> list[Path]:
    txt_files = sorted(transformed_dir.glob("*.txt"))
    if txt_files:
        return txt_files

    zip_files = sorted(transformed_dir.glob("*.zip"))
    for z in zip_files:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(transformed_dir)

    return sorted(transformed_dir.glob("*.txt"))


@app.function(
    image=image,
    secrets=[gcp_secret],
    timeout=60 * 60 * 8,
    volumes={str(VOLUME_MOUNT): volume},
)
def upload_transformed_txt_to_rag_corpus(
    storage_path: str = "/vol/officeqa/repo",
    corpus_display_name: str | None = None,
    max_files: int | None = None,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    log_every: int = 25,
) -> str:
    _ensure_google_application_credentials()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION") or os.environ.get("GCP_LOCATION")
    if not project:
        raise RuntimeError("Missing GOOGLE_CLOUD_PROJECT (or GCP_PROJECT)")
    if not location:
        raise RuntimeError("Missing GOOGLE_CLOUD_LOCATION (or GCP_LOCATION)")

    import vertexai
    from vertexai.preview import rag

    vertexai.init(project=project, location=location)

    display_name = corpus_display_name or f"officeqa-transformed-txt-{int(time.time())}"
    corpus = rag.create_corpus(display_name=display_name)

    transformed_dir = Path(storage_path) / "treasury_bulletins_parsed" / "transformed"
    if not transformed_dir.exists():
        raise FileNotFoundError(str(transformed_dir))

    txt_files = _load_transformed_txt_files(transformed_dir)
    if not txt_files:
        raise RuntimeError(f"No .txt files found in {transformed_dir}")
    if max_files is not None:
        txt_files = txt_files[:max_files]

    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ),
    )

    total = len(txt_files)
    for i, path in enumerate(txt_files, start=1):
        rag.upload_file(
            corpus_name=corpus.name,
            path=str(path),
            display_name=path.name,
            transformation_config=transformation_config,
        )
        if log_every > 0 and (i % log_every == 0 or i == total):
            print(f"Uploaded {i}/{total}")

    return corpus.name


@app.local_entrypoint()
def main(
    storage_path: str = "/vol/officeqa/repo",
    corpus_display_name: str | None = None,
    max_files: int | None = None,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
) -> None:
    corpus_id = upload_transformed_txt_to_rag_corpus.remote(
        storage_path=storage_path,
        corpus_display_name=corpus_display_name,
        max_files=max_files,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    print(corpus_id)
