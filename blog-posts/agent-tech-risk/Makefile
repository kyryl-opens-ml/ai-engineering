.PHONY: export upload dataset

export:
	uv run risk-generator export-hf cases/

upload:
	uv run hf upload koml/agent-tech-risk-cases dataset.jsonl --repo-type dataset
	uv run hf upload koml/agent-tech-risk-cases dataset_card.md README.md --repo-type dataset

dataset: export upload
