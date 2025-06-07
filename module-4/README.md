# Module 4

![Pipelines](./../docs/pipelines.jpg)

## Overview

This module demonstrates pipeline orchestration using Dagster.

## Practice

Build end-to-end training and inference pipelines using Dagster.

### Key tasks

- Implement your pipeline logic in Dagster.

***




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

- Update the Google Doc with the pipeline section for your use case.
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
