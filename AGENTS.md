# Contributor Guide

This repository contains homework solutions for the [ML in Production](https://edu.kyrylai.com/courses/ml-in-production) course.  Each module under `module-*` holds an independent example or exercise.

## Development
- Use Python 3.10+.
- Format Python code using `ruff format` and check style with `ruff check`.
- Execute tests with `pytest` from the repository root. Some modules provide Makefiles with helper commands such as `make test`.
- Ensure all tests pass before committing.

## Pull Requests
- Keep PR titles concise, e.g. `[module-x] <short description>`.
- Summarize the changes in the body of the PR.

## Cursor Cloud specific instructions

### Repository overview
Multi-module ML course repo. Each `module-*` directory is independent with its own deps. `blog-posts/` contains supplemental projects outside the main curriculum. Module 8 is documentation-only.

### Dependency management
- **Modules 1–2**: managed by `uv` (`pyproject.toml` + `uv.lock`). Install with `uv sync` inside the module directory.
- **Modules 3–7**: use `requirements.txt` (pip). Install into the shared `.venv` with `uv pip install -r <module>/requirements.txt`.
- No root-level dependency file; the update script installs a base set into `/workspace/.venv`.

### Running the module-5 FastAPI service
The predictor loads a model from `/tmp/model`. Without W&B credentials, bootstrap a local model first:
```bash
source /workspace/.venv/bin/activate
python -c "
from transformers import AutoModelForSequenceClassification, AutoTokenizer
t = AutoTokenizer.from_pretrained('distilbert-base-uncased')
m = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
t.save_pretrained('/tmp/model'); m.save_pretrained('/tmp/model')
"
cd module-5
WANDB_MODE=disabled uvicorn serving.fast_api:app --host 0.0.0.0 --port 8080
```

### Lint / format / test
```bash
ruff check                           # lint all modules
ruff format --check                  # format check
cd module-5 && WANDB_MODE=disabled pytest tests/ -v  # module-5 tests (needs /tmp/model)
```

### Known gotchas
- `wandb` 0.17.x requires `protobuf<5`. The update script pins this.
- `httpx` must be `<0.28` for FastAPI 0.109.2's `TestClient` to work.
- Many modules need Docker, GPU, or external API keys (W&B, OpenAI) for full functionality; the local dev setup covers CPU-only Python workflows.
