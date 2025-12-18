# officeqa-poc

Minimal Modal utility that clones `databricks/officeqa` into a shared volume for downstream processing.

## Requirements
- `uv` (already configured via this project)
- Modal account credentials exposed as `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`
- Optional: `OFFICEQA_VOLUME_NAME` to override the target Modal volume (defaults to `officeqa-data`)

## Install dependencies
```bash
uv sync
```

## Pull the OfficeQA data
```bash
MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=... uv run modal run modal_officeqa_setup.py --branch main
```
- The script clones the repo into `/share/officeqa` inside the shared volume, replacing previous contents on each run.
- Pass a different branch name with `--branch <branch>` when needed.
