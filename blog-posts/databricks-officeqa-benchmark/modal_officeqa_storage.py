import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import modal

REPO_URL = "https://github.com/databricks/officeqa.git"
DEFAULT_VOLUME_NAME = "officeqa-data"
DEFAULT_EXPECTED_PDF_COUNT = 696
VOLUME_MOUNT = Path("/vol")
ROOT_DIR = VOLUME_MOUNT / "officeqa"
REPO_DIR = ROOT_DIR / "repo"
MANIFEST_PATH = ROOT_DIR / "manifest.json"


def _require_modal_creds() -> None:
    required = ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")


def _run(
    cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def _is_lfs_pointer(path: Path) -> bool:
    with path.open("rb") as f:
        head = f.read(200)
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def _walk_files(root: Path, *, exclude_dirs: set[str]) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for name in filenames:
            files.append(Path(dirpath) / name)
    return files


def _stats_for_dir(path: Path, *, suffix: str | None = None) -> dict[str, int]:
    count = 0
    total_bytes = 0
    lfs_pointers = 0
    if not path.exists():
        return {"count": 0, "bytes": 0, "lfs_pointers": 0}
    for p in _walk_files(path, exclude_dirs={".git"}):
        if suffix and p.suffix != suffix:
            continue
        count += 1
        total_bytes += p.stat().st_size
        if _is_lfs_pointer(p):
            lfs_pointers += 1
    return {"count": count, "bytes": total_bytes, "lfs_pointers": lfs_pointers}


def _repo_manifest(repo_dir: Path, *, expected_pdf_count: int) -> dict[str, object]:
    files = _walk_files(repo_dir, exclude_dirs={".git"})
    total_bytes = sum(p.stat().st_size for p in files)
    pdf_stats = _stats_for_dir(repo_dir / "treasury_bulletin_pdfs", suffix=".pdf")
    parsed_zip_stats = _stats_for_dir(
        repo_dir / "treasury_bulletins_parsed", suffix=".zip"
    )
    lfs_pointer_files = sum(1 for p in files if _is_lfs_pointer(p))

    if pdf_stats["count"] != expected_pdf_count:
        raise RuntimeError(
            f"Expected {expected_pdf_count} PDFs, found {pdf_stats['count']} in treasury_bulletin_pdfs/"
        )
    if pdf_stats["lfs_pointers"] != 0:
        raise RuntimeError(
            "Some PDFs look like Git LFS pointer files (git lfs pull likely failed)"
        )
    if parsed_zip_stats["lfs_pointers"] != 0:
        raise RuntimeError(
            "Some parsed zip files look like Git LFS pointer files (git lfs pull likely failed)"
        )

    commit = (
        subprocess.check_output(["git", "-C", str(repo_dir), "rev-parse", "HEAD"])
        .decode()
        .strip()
    )

    return {
        "repo_url": REPO_URL,
        "commit": commit,
        "generated_at_unix": int(time.time()),
        "repo_worktree": {
            "count": len(files),
            "bytes": total_bytes,
            "lfs_pointers": lfs_pointer_files,
        },
        "treasury_bulletin_pdfs": pdf_stats,
        "treasury_bulletins_parsed_zips": parsed_zip_stats,
        "expected_pdf_count": expected_pdf_count,
    }


volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)
image = modal.Image.debian_slim().apt_install("git", "git-lfs", "ca-certificates")
app = modal.App("officeqa-storage")


@app.function(
    image=image,
    timeout=60 * 60 * 8,
    volumes={str(VOLUME_MOUNT): volume},
)
def pull(
    *, force: bool = False, expected_pdf_count: int = DEFAULT_EXPECTED_PDF_COUNT
) -> dict[str, object]:
    ROOT_DIR.mkdir(parents=True, exist_ok=True)

    if force and REPO_DIR.exists():
        shutil.rmtree(REPO_DIR)

    if REPO_DIR.exists():
        _run(["git", "-C", str(REPO_DIR), "fetch", "--all", "--tags", "--prune"])
        _run(["git", "-C", str(REPO_DIR), "checkout", "main"])
        _run(["git", "-C", str(REPO_DIR), "pull", "--ff-only"])
    else:
        env = dict(os.environ)
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        _run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], env=env)

    _run(["git", "-C", str(REPO_DIR), "lfs", "install", "--local"])
    _run(["git", "-C", str(REPO_DIR), "lfs", "pull"])

    manifest = _repo_manifest(REPO_DIR, expected_pdf_count=expected_pdf_count)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    volume.commit()
    return manifest


@app.function(
    image=image,
    timeout=60 * 60,
    volumes={str(VOLUME_MOUNT): volume},
)
def verify(
    *, expected_pdf_count: int = DEFAULT_EXPECTED_PDF_COUNT
) -> dict[str, object]:
    if not REPO_DIR.exists():
        raise RuntimeError("Repo not found on volume. Run pull first.")
    if not MANIFEST_PATH.exists():
        raise RuntimeError("Manifest not found on volume. Run pull first.")

    previous = json.loads(MANIFEST_PATH.read_text())
    current = _repo_manifest(REPO_DIR, expected_pdf_count=expected_pdf_count)

    if previous["commit"] != current["commit"]:
        raise RuntimeError(
            f"Commit changed: {previous['commit']} -> {current['commit']}"
        )
    if previous["repo_worktree"] != current["repo_worktree"]:
        raise RuntimeError("Worktree stats changed since last pull")
    if previous["treasury_bulletin_pdfs"] != current["treasury_bulletin_pdfs"]:
        raise RuntimeError("PDF stats changed since last pull")
    if (
        previous["treasury_bulletins_parsed_zips"]
        != current["treasury_bulletins_parsed_zips"]
    ):
        raise RuntimeError("Parsed zip stats changed since last pull")

    return current


@app.local_entrypoint()
def main(
    action: str = "pull",
    force: bool = False,
    expected_pdf_count: int = DEFAULT_EXPECTED_PDF_COUNT,
) -> None:
    _require_modal_creds()
    if action == "pull":
        manifest = pull.remote(force=force, expected_pdf_count=expected_pdf_count)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return
    if action == "verify":
        manifest = verify.remote(expected_pdf_count=expected_pdf_count)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return
    raise RuntimeError("action must be 'pull' or 'verify'")
