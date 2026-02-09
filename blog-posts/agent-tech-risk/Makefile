.PHONY: format lint test export upload dataset publish

# Code quality
format:
	uv run ruff format packages/ tests/

lint:
	uv run ruff check packages/ tests/

test:
	uv run pytest tests/ -v

# Dataset
export:
	uv run risk-generator export-hf cases/

upload:
	uv run hf upload koml/agent-tech-risk-cases dataset.jsonl --repo-type dataset
	uv run hf upload koml/agent-tech-risk-cases dataset_card.md README.md --repo-type dataset

dataset: export upload

# Publish (set UV_PUBLISH_TOKEN or pass --token)
# Get token at: https://pypi.org/manage/account/token/
publish:
	cd packages/risk-generator && uv build && uv publish --token $(UV_PUBLISH_TOKEN)
	cd packages/risk-discovery && uv build && uv publish --token $(UV_PUBLISH_TOKEN)
