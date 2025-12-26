# databricks-officeqa-benchmark

Experiments and tooling to reproduce and extend the Databricks OfficeQA benchmark workflow (data ingestion, corpus creation for RAG, and evaluation).

Reference: [Introducing the OfficeQA benchmark: End-to-end grounded reasoning](https://www.databricks.com/blog/introducing-officeqa-benchmark-end-to-end-grounded-reasoning)

## Setup

Requirements:
- Python 3.10+
- `uv`

Install dependencies:

```bash
make install
```

Run tests:

```bash
make test
```

Lint and format:

```bash
make lint
make format
```

## OfficeQA data on Modal Volume

This downloads the `databricks/officeqa` repo and all Git LFS data (including `treasury_bulletin_pdfs/`, ~20GB) into a shared Modal Volume at `/vol/officeqa/repo` and writes an integrity manifest to `/vol/officeqa/manifest.json` (file counts + total bytes).

```bash
export MODAL_TOKEN_ID=...
export MODAL_TOKEN_SECRET=...
export OFFICEQA_VOLUME=officeqa-data

uv run modal run modal_officeqa_storage.py --action pull
uv run modal run modal_officeqa_storage.py --action verify
```

To re-download from scratch:

```bash
uv run modal run modal_officeqa_storage.py --action pull --force true
```

## Gemini File Search corpus creation

This creates a Gemini File Search store and uploads files from `storage_path` (including the OfficeQA Modal Volume mounted at `/vol`).

```bash
modal secret create gemini GEMINI_API_KEY=...
uv run modal run src/databricks_officeqa_benchmark/modal_file_search.py --storage-path /vol/officeqa/repo
```

## Roadmap

0. Setup
- Repo setup: `https://github.com/kyryl-opens-ml/agent-sandbox-officeqa`
- Model account setup: storage 
- GCP account setup: file api 
- Make sure to add all accounts you need for this project, and know how you plan to use them and in which case.

1. Python project setup
Implement UV style python project with readme, package name, makefile and test.
- `uv init` with proper pyproject.toml
- Makefile with: install, test, lint, format targets
- Basic pytest setup with one passing test
- README with project overview and setup instructions

2. Data ingestion
Pull and setup storage for `https://github.com/databricks/officeqa/tree/main`
I want to have a simple modal script to setup this repo and pull all data.
- Write simple modal app to pull this repo and clone data to shared volume
- Read modal creds from env vars
- Verify data integrity after pull (file counts, sizes)

3. RAG creating functionality
Based on `https://ai.google.dev/gemini-api/docs/file-search`
Write python function which reads data from storage and uploads it to File Search tool.
- Structure as modal function
- Add Gemini creds to modal secrets
- Return corpus ID for later querying

4. Evaluation baseline
Implement eval function for simple LLM (no RAG, just prompting).
- Read QA pairs from modal storage
- Run inference with base Gemini
- Run inference with random baseline (for fast verification)
- Calculate accuracy, F1, exact match
- Print metrics to CLI, save results to JSON

```bash
modal secret create gemini GEMINI_API_KEY=...
uv run modal run src/databricks_officeqa_benchmark/modal_eval_simple.py --max-questions 10 --out-path results.json
```

5. RAG ingestion: Raw PDFs
Upload raw PDFs to GCP RAG corpus.
Based on `treasury_bulletin_pdfs/` (~20GB, 696 files)
- Direct PDF upload, let Gemini handle parsing
- Modal function with GCP creds
- Track upload status and corpus stats
- Return corpus ID

6. RAG ingestion: Parsed JSON
Upload pre-parsed JSON to GCP RAG corpus.
Based on `treasury_bulletins_parsed/jsons/` (~600MB)
- Unzip archives first (use provided `unzip.py`)
- Structure as text chunks with metadata (bounding boxes, tables as HTML)
- Modal function, separate corpus from task 5
- Return corpus ID

7. RAG ingestion: Transformed TXT
Upload transformed text files to GCP RAG corpus.
Based on `treasury_bulletins_parsed/transformed/` (~200MB)
- Markdown tables, cleaner text, LLM-friendly format
- Modal function, separate corpus from tasks 5-6
- Return corpus ID

8. RAG evaluation suite
Eval functions for LLM + RAG combinations.
- Test each ingestion variant (v1, v2, v3)
- Test combinations (e.g., v1+v2 merged corpus)
- Same metrics as baseline, plus retrieval recall
- Compare against baseline, output delta table

9. DSPy optimization
Based on `https://dspy.ai/`
- Define signature for QA task
- Implement retrieval module with GCP RAG
- Run BootstrapFewShot or MIPRO optimization
- Save optimized program to modal volume

10. DSPy evaluation
- Run optimized DSPy program on test set
- Compare against baseline and vanilla RAG
- Track prompt tokens used (cost analysis)

11. LLM fine-tuning
Fine-tune Gemini on officeqa training split.
- Prepare training data in required format
- Use Vertex AI fine-tuning API
- Track training metrics, save model endpoint

12. Fine-tuned model evaluation
- Run fine-tuned model on test set
- Test with and without RAG
- Compare against all previous approaches

13. Reporting and error analysis
- Aggregate all experiment results
- Generate comparison table (baseline vs RAG vs DSPy vs fine-tuned)
- Error categorization: retrieval failures, reasoning failures, format issues
- Export to markdown report + CSV for further analysis