.PHONY: find verify visualize dagster

find:
	uv run ./app/find.py --save-to results-simple-base.json

verify:
	uv run ./app/verify.py --input-file results-simple-base.json --output-file results-simple-base-verify.json

visualize:
	uv run ./app/visualize.py --input-file results-simple-base-verify.json
