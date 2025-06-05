# Module 2

![Data management](./../docs/data.jpg)

## Overview

This module covers data storage and processing.
benchmark data formats and explore streaming datasets and vector databases.

## Practice

[Practice task](./PRACTICE.md)

---

## Reference implementation

---


# Pandas profiling

<https://aaltoscicomp.github.io/python-for-scicomp/data-formats/>

![alt text](./images/pandas-formats.png)


# CVS inference performance

Run experiments.

```bash
python processing/inference_example.py run-single-worker --inference-size 10000000
python processing/inference_example.py run-pool --inference-size 10000000
python processing/inference_example.py run-ray --inference-size 10000000
```

Results.

| Name of Inference    | Time (seconds)      |
|----------------------|---------------------|
| Inference 1 worker   | 12.64  |
| Inference 16 workers (ThreadPoolExecutor) | 0.85  |
| Inference 16 workers (ProcessPoolExecutor) | 4.03  |
| Inference with Ray   | 2.19  |


# Streaming dataset


Create

```bash
python streaming-dataset/mock_data.py create-data --path-to-save random-data
```

Upload

```bash
aws s3api create-bucket --bucket datasets
aws s3 cp --recursive random-data s3://datasets/random-data
```

Read

```bash
python streaming-dataset/mock_data.py get-dataloader --remote random-data
```

Alternatives:

- <https://www.tensorflow.org/tutorials/load_data/tfrecord>
- <https://github.com/aws/amazon-s3-plugin-for-pytorch>
- <https://pytorch.org/blog/efficient-pytorch-io-library-for-large-datasets-many-files-many-gpus/>
- <https://github.com/webdataset/webdataset>
- <https://github.com/mosaicml/streaming>
- <https://github.com/huggingface/datatrove>

# Vector Databases

Create database.

```bash
python vector-db/rag_cli_application.py create-new-vector-db --table-name test --number-of-documents 300
```

Query database.

```bash
python vector-db/rag_cli_application.py query-existing-vector-db  --query 'complex query' --table-name test
```

Storage [diagram](https://lancedb.github.io/lancedb/concepts/storage/)


# DVC

Init DVC

```bash
dvc init --subdir
git status
git commit -m "Initialize DVC"
```

Add data

```bash
mkdir data
touch ./data/big-data.csv
```

Add to dvc

```bash
dvc add ./data/big-data.csv
git add data/.gitignore data/big-data.csv.dvc
git commit -m "Add raw data"
```
Add remote

```bash
dvc remote add -d storage s3://ml-data
```



Save code to git

```bash
git add .dvc/config
git commit -m "Configure remote storage"
git push 
```

Save data to storage

```bash
dvc push
```

- <https://dvc.org/doc/start/data-management>
- <https://github.com/iterative/dataset-registry>

## Labeling with Argilla

```bash
docker run -it --rm --name argilla -p 6900:6900 argilla/argilla-quickstart:v2.0.0rc1
```

User/Password you can find [here](https://github.com/argilla-io/argilla/blob/v2.0.0rc1/argilla-server/docker/quickstart/Dockerfile#L60-L62).

Alternatives on: [K8S](https://github.com/argilla-io/argilla/tree/develop/examples/deployments/k8s) or [Railway](https://railway.app/template/KNxfha?referralCode=_Q3XIe)

Create simple dataset:

```bash
uv run ./labeling/create_dataset.py
```

Create synthetic dataset:

```bash
uv run ./labeling/create_dataset_synthetic.py
```

## MCP with DuckDB

```

```

## Updated design doc

[Google doc](https://docs.google.com/document/d/1dEzWd3pPozmU3AhMXjW3xcONUeNJee53djilN1A-wR8/edit)
