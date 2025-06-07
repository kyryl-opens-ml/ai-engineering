# Module 4

![Pipelines](./../docs/pipelines.jpg)

## Overview

This module demonstrates pipeline orchestration using Airflow
and Dagster.

## Practice

Build end-to-end training and inference pipelines using Airflow and Dagster.

### Key tasks

- Deploy Airflow with KubernetesPodOperator.
- Implement the same logic in Dagster.

***


# H7: AirFlow pipelines

## Reading list:

- [How we Reduced our ML Training Costs by 78%!!](https://blog.gofynd.com/how-we-reduced-our-ml-training-costs-by-78-a33805cb00cf)
- [Leveraging the Pipeline Design Pattern to Modularize Recommendation Services](https://doordash.engineering/2021/07/07/pipeline-design-pattern-recommendation/)
- [Why data scientists shouldn’t need to know Kubernetes](https://huyenchip.com/2021/09/13/data-science-infrastructure.html)
- [Orchestration for Machine Learning](https://madewithml.com/courses/mlops/orchestration/)
- [KubernetesPodOperator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html)


## Task:

For this task, you will need both a training and an inference pipeline. The training pipeline should include at least the following steps: Load Training Data, Train Model, Save Trained Models. Additional steps may be added as desired. Similarly, the inference pipeline should include at least the following steps: Load Data for Inference, Load Trained Model, Run Inference, Save Inference Results. You may also add extra steps to this pipeline as needed.


- PR4: Write a README with instructions on how to deploy Airflow.
- PR5: Write an Airflow training pipeline.
- PR6: Write an Airflow inference pipeline.


## Criteria:

- 6 PRs merged.


# H8: Dagster

## Reading list:

- [Orchestrating Machine Learning Pipelines with Dagster](https://dagster.io/blog/dagster-ml-pipelines)
- [ML pipelines for fine-tuning LLMs](https://dagster.io/blog/finetuning-llms)
- [Awesome open source workflow engines](https://github.com/meirwah/awesome-workflow-engines)
- [A framework for real-life data science and ML](https://metaflow.org/)
- [New in Metaflow: Train at scale with AI/ML frameworks](https://outerbounds.com/blog/distributed-training-with-metaflow/)
- [House all your ML orchestration needs](https://flyte.org/machine-learning)


## Task:

For this task, you will need both a training and an inference pipeline. The training pipeline should include at least the following steps: Load Training Data, Train Model, Save Trained Models. Additional steps may be added as desired. Similarly, the inference pipeline should include at least the following steps: Load Data for Inference, Load Trained Model, Run Inference, Save Inference Results. You may also add extra steps to this pipeline as needed.

- Update the Google Doc with the pipeline section for your use case, and compare Airflow and Dagster.
- PR1: Write a Dagster training pipeline.
- PR2: Write a Dagster inference pipeline.

## Criteria:


- 2 PRs merged.
- Pipeline section in the google doc.

---

## Reference implementation

---

# Setup

Create kind cluster

```bash
kind create cluster --name ml-in-production
```

Run k9s

```bash
k9s -A
```

# Airflow

Install

```bash
AIRFLOW_VERSION=2.9.3
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install apache-airflow-providers-cncf-kubernetes==8.3.3
```

Run standalone airflow

```bash
export AIRFLOW_HOME=$PWD/airflow_pipelines
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export WANDB_PROJECT=****************
export WANDB_API_KEY=****************
airflow standalone
```

Create storage

```bash
kubectl create -f ./airflow_pipelines/volumes.yaml
```

Open UI

```bash
open http://0.0.0.0:8080
```

Trigger training job.

```bash
airflow dags trigger training_dag
```

Trigger 5 training jobs.

```bash
for i in {1..5}; do airflow dags trigger training_dag; sleep 1; done
```

Trigger inference job.

```bash
airflow dags trigger inference_dag
```

Trigger 5 inference jobs.

```bash
for i in {1..5}; do airflow dags trigger inference_dag; sleep 1; done
```

### References:
- [AI + ML examples of DAGs](https://registry.astronomer.io/dags?categoryName=AI+%2B+Machine+Learning&limit=24&sorts=updatedAt%3Adesc)
- [Pass data between tasks](https://www.astronomer.io/docs/learn/airflow-passing-data-between-tasks)


# Dagster


Setup

```bash
mkdir ./dagster_pipelines/dagster-home
export DAGSTER_HOME=$PWD/dagster_pipelines/dagster-home
export WANDB_PROJECT=****************
export WANDB_API_KEY=****************
```

Deploy modal functions

```bash
MODAL_FORCE_BUILD=1 modal deploy ./dagster_pipelines/text2sql_functions.py
```

Run Dagster

```bash
dagster dev -f dagster_pipelines/text2sql_pipeline.py -p 3000 -h 0.0.0.0
```

### References:

- [Introducing Asset Checks](https://dagster.io/blog/dagster-asset-checks)
- [Anomaly Detection](https://dagster.io/glossary/anomaly-detection)


## Updated design doc

[Google doc](https://docs.google.com/document/d/1j9-RFCrLRQy54TsywHxvje56EuntAbUbSlw_POsWl5Q/edit?usp=sharing)
