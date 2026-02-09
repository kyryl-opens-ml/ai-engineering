# AGENTS.md

## Project overview

This is a uv workspace with two Python packages for AWS technical risk assessment in PE due diligence:

- **risk-generator** (`packages/risk-generator/`) — generates synthetic AWS infrastructure cases with embedded risks, deploys to LocalStack, exports to HuggingFace
- **risk-discovery** (`packages/risk-discovery/`) — Pydantic AI agent that scans AWS/LocalStack environments to find risks, plus evaluation framework

Dataset: https://huggingface.co/datasets/koml/agent-tech-risk-cases

## Setup

```bash
uv sync                          # install all workspace packages + dev deps
cp .env.example .env             # add AWS_REGION, AWS credentials for Bedrock
```

## Build and test

```bash
uv run pytest tests/ -v          # run all tests (28 tests, no network needed)
uv run ruff check packages/ tests/   # lint
uv run ruff format packages/ tests/  # format
```

Always run tests before committing. All tests must pass.

## Project structure

```
pyproject.toml                   # workspace root
packages/
  risk-generator/
    pyproject.toml               # published as `risk-generator` on PyPI
    src/risk_generator/
      categories.py              # 15 risk categories (tr1-tr15), localstack_free flag
      models.py                  # 10 company profile presets
      generator.py               # Claude Agent SDK case generation
      deployer.py                # deploy aws_state.json to LocalStack (7 services)
      cli.py                     # CLI: create, batch, deploy, export-hf, config
  risk-discovery/
    pyproject.toml               # published as `risk-discovery` on PyPI, depends on risk-generator
    src/risk_discovery/
      models.py                  # RiskFinding, ScanResult (pydantic models)
      agent.py                   # Pydantic AI agent with boto3 code execution tool
      eval.py                    # HF dataset loading, risk matching, model evaluation
      cli.py                     # CLI: infer, eval
tests/
  test_generator.py              # categories, deployer, case file validation
  test_discovery.py              # matching logic, models
scripts/
  run_eval.py                    # reproducible evaluation across 4 Bedrock models
  debug_cases.py                 # deploy all cases to kind cluster
cases/                           # 10 generated cases (aws_state.json + risks.yaml each)
```

## Key patterns

- **PascalCase** for all AWS state JSON fields (`RoleName`, `PolicyDocument`, `IngressRules`)
- **`get_field(obj, *keys, default=None)`** in deployer.py tries multiple key formats (PascalCase, snake_case)
- **LocalStack free tier only**: iam, s3, ec2, lambda, dynamodb, secretsmanager, sqs. Never use rds, eks, elasticache, ecs, cloudfront
- **Risk categories**: tr1-tr15. Categories tr6, tr7, tr10, tr11, tr12 require LocalStack Pro — use `LOCALSTACK_FREE_CATEGORIES` for free-tier work
- **Bedrock models** use `us.` inference profile prefix: `bedrock:us.anthropic.claude-opus-4-5-20251101-v1:0`
- **Two-pass risk matching**: first by category+resource, then resource-only fallback (agent may use different but valid categories)
- **Eval errors count as 0** in averaging, not excluded — prevents inflated scores for models that fail on hard cases

## Code style

- Python 3.12+
- Ruff for linting and formatting (default config)
- Pydantic v2 models, dataclasses for simple containers
- Typer for CLI, Rich for output
- Keep code minimal — no over-engineering, no unnecessary abstractions

## Common workflows

```bash
# Generate a new case and validate it
uv run risk-generator create

# Deploy a case to LocalStack and scan it
uv run risk-generator deploy cases/case_payflow --keep
uv run risk-discovery infer http://localhost:PORT
docker rm -f localstack-risk-PORT

# Run full model evaluation (needs Bedrock credentials)
uv run python scripts/run_eval.py --output results.json

# Publish packages
UV_PUBLISH_TOKEN=pypi-xxx make publish
```

## Security

- Never commit `.env` files — they contain AWS credentials and Bedrock tokens
- `.env` is excluded from package builds via `hatch.build.targets.sdist.exclude`
- Generated cases may contain fake secrets (Slack webhooks, API keys) — these are synthetic but may trigger GitHub push protection
