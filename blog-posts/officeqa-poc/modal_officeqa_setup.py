import os
import pathlib
import shutil
import subprocess

import modal

MODAL_TOKEN_ID = os.environ.get("MODAL_TOKEN_ID")
MODAL_TOKEN_SECRET = os.environ.get("MODAL_TOKEN_SECRET")
if not MODAL_TOKEN_ID or not MODAL_TOKEN_SECRET:
    raise RuntimeError("Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET")

REPO_URL = "https://github.com/databricks/officeqa.git"
BRANCH = "main"
VOLUME_NAME = os.environ.get("OFFICEQA_VOLUME_NAME", "officeqa-data")
TARGET_DIR = pathlib.Path("/share/officeqa")

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
image = modal.Image.debian_slim().apt_install("git", "git-lfs")
app = modal.App("officeqa-setup", image=image)


def _clone(branch: str):
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    subprocess.run(
        ["git", "clone", "--branch", branch, "--single-branch", REPO_URL, str(TARGET_DIR)],
        check=True,
    )
    subprocess.run(["git", "-C", str(TARGET_DIR), "lfs", "install"], check=True)
    subprocess.run(["git", "-C", str(TARGET_DIR), "lfs", "pull"], check=False)


@app.function(volumes={"/share": volume}, timeout=600)
def sync(branch: str = BRANCH):
    _clone(branch)


@app.local_entrypoint()
def main(branch: str = BRANCH):
    sync.call(branch)
