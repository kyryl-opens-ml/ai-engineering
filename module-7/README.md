# Module 7

![Monitoring](./../docs/monitoring.jpg)

## Overview

This module sets up observability for ML applications using SigNoz,
Grafana and Seldon analytics.

## Practice

Integrate monitoring tools and add drift detection to your pipelines.

### Key tasks

- Instrument your app with SigNoz.
- Create a Grafana dashboard.
- Add simple drift detection logic.

***


# H13: Monitoring and observability

## Reading list: 

- [Underspecification Presents Challenges for Credibility in Modern Machine Learning](https://arxiv.org/abs/2011.03395)
- [Why is pattern recognition often defined as an ill-posed problem?](https://stats.stackexchange.com/questions/433692/why-is-pattern-recognition-often-defined-as-an-ill-posed-problem)
- [How ML Breaks: A Decade of Outages for One Large ML Pipeline](https://www.usenix.org/conference/opml20/presentation/papasian)
- [Elastic Stack](https://www.elastic.co/elastic-stack)
- [Real-time Interactive Dashboards DataDog](https://www.datadoghq.com/product/platform/dashboards/)
- [Python OpenTelemetry Instrumentation](https://signoz.io/docs/instrumentation/python/)
- [Opentelemetry Devstats](https://opentelemetry.devstats.cncf.io/d/4/company-statistics-by-repository-group?orgId=1)
- [Log Monitoring 101 Detailed Guide [Included 10 Tips]](https://signoz.io/blog/log-monitoring/)
- [Lecture 10: Data Distribution Shifts & Monitoring Presentation](https://docs.google.com/presentation/d/1tuCIbk9Pye-RK1xqiiZXPzT8lIgDUL6CqBkFSYZXkbY/edit#slide=id.p)
- [Lecture 10. Data Distribution Shifts and Monitoring Notes](https://docs.google.com/document/d/14uX2m9q7BUn_mgnM3h6if-s-r0MZrvDb-ZHNjgA1Uyo/edit#heading=h.sqk67ofnp3ir)
- [Data Distribution Shifts and Monitoring](https://huyenchip.com/2022/02/07/data-distribution-shifts-and-monitoring.html)
- [Monitoring Machine Learning Systems Made with ML](https://madewithml.com/courses/mlops/monitoring/)
- [Inferring Concept Drift Without Labeled Data](https://concept-drift.fastforwardlabs.com/)
- [Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift](https://arxiv.org/abs/1810.11953)
- [The Playbook to Monitor Your Model’s Performance in Production](https://towardsdatascience.com/the-playbook-to-monitor-your-models-performance-in-production-ec06c1cc3245)
- [Ludwig](https://ludwig.ai/latest/)
- [Declarative Machine Learning Systems](https://arxiv.org/pdf/2107.08148.pdf)
- [Deploy InferenceService with Alibi Outlier/Drift Detector](https://kserve.github.io/website/0.10/modelserving/detect/alibi_detect/alibi_detect/)

## Task:



- PR1: Write code for integrating SigNoz monitoring into your application.
- PR2: Write code for creating a Grafana dashboard for your application.
- PR3: Write code for detecting drift in your pipeline using Dagster within your input and output features.
- Update the Google document with system monitoring and a plan for ML monitoring, covering aspects like ground truth availability, drift detection, etc.

## Criteria: 

- 3 PRs merged 
- Monitoring plan for system and ML in the google doc.

# H14: Tools, LLMs and Data moat.

## Reading list:


- [Alibi Detect](https://github.com/SeldonIO/alibi-detect)
- [Evidently](https://github.com/evidentlyai/evidently)
- [A Guide to Monitoring Machine Learning Models in Production](https://developer.nvidia.com/blog/a-guide-to-monitoring-machine-learning-models-in-production/)
- [Top 7 ML Model Monitoring Tools in 2024](https://www.qwak.com/post/top-ml-model-monitoring-tools)
- [Best Tools to Do ML Model Monitoring](https://neptune.ai/blog/ml-model-monitoring-best-tools)
- [DataDog Machine Learning](https://www.datadoghq.com/solutions/machine-learning/)
- [Another tool won’t fix your MLOps problems](https://dshersh.medium.com/too-many-mlops-tools-c590430ba81b)
- [LLMOps](https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/llmops/)
- [LangSmith Docs](https://www.langchain.com/langsmith)
- [RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback](https://arxiv.org/abs/2309.00267)
- [OpenLLMetry](https://github.com/traceloop/openllmetry?tab=readme-ov-file)
- [Open-source ML observability course](https://github.com/evidentlyai/ml_observability_course)
- [RLHF: Reinforcement Learning from Human Feedback](https://huyenchip.com/2023/05/02/rlhf.html)


## Task:

- PR1: Write code for utilizing a managed model monitoring tool for your model (e.g., Arize).
- PR2: Write code for LLM monitoring with the help of Langsmith or similar tools.
- PR3: Write code to close the loop: create a dataset for labeling from your monitoring solution.
- Update the Google document with the data moat strategy, detailing how you would enrich data from production and reuse it for building future models.


## Criteria:


- 3 PRs are merged 
- Data moat strategy in the google doc.

---

## Reference implementation

---



# Setup 

Create kind cluster 

```
kind create cluster --name ml-in-production
```

Run k9s 

```
k9s -A
```

# LLM Observability

https://docs.google.com/presentation/d/13ePQfvgSPioMmDN0OOQklvX7PQQ4RcEVCWm9ljum4aU/edit#slide=id.g2f7f3a46425_0_422


## Apps

Setup

```
export PYTHONPATH=llm-apps/AI-Scientist/
export TRACELOOP_BASE_URL="http://localhost:4318"
export OPENAI_API_KEY=sk-proj-****
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=lsv2_-****
```

Run SQL

```
python llm-apps/sql_app.py
```

Run AI-Scientist

```
python llm-apps/reviewer.py
```

## SigNoz 


Install 

```
DEFAULT_STORAGE_CLASS=$(kubectl get storageclass -o=jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}')
kubectl patch storageclass "$DEFAULT_STORAGE_CLASS" -p '{"allowVolumeExpansion": true}'

helm repo add signoz https://charts.signoz.io
helm repo list
helm install my-release signoz/signoz
```

Access:

```
kubectl port-forward svc/my-release-signoz-frontend 3301:3301
kubectl port-forward svc/my-release-signoz-otel-collector 4318:4318
```

# Grafana 


```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack

kubectl port-forward --address 0.0.0.0 svc/monitoring-grafana 3000:80
admin/prom-operator

helm uninstall monitoring 
```

- Reference: https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/README.md


# Data monitoring 

- https://github.com/evidentlyai/evidently
- https://github.com/SeldonIO/alibi-detect
- https://github.com/whylabs/whylogs
- https://github.com/GokuMohandas/monitoring-ml


## Seldon: Monitoring and explainability of models in production


[Monitoring and explainability of models in production](https://arxiv.org/abs/2007.06299)
[Desiderata for next generation of ML model serving](https://arxiv.org/abs/2210.14665)


Setup seldon 

https://github.com/SeldonIO/seldon-core/tree/v2/ansible


Ansible install 

```
pip install ansible openshift docker passlib
ansible-galaxy collection install git+https://github.com/SeldonIO/ansible-k8s-collection.git
```


Clone repo 

```
git clone https://github.com/SeldonIO/seldon-core --branch=v2

ansible-playbook playbooks/kind-cluster.yaml
ansible-playbook playbooks/setup-ecosystem.yaml
ansible-playbook playbooks/setup-seldon.yaml
```

CLI client 

```
wget https://github.com/SeldonIO/seldon-core/releases/download/v2.7.0-rc1/seldon-linux-amd64
mv seldon-linux-amd64 seldon
chmod u+x seldon
sudo mv ./seldon /usr/local/bin/seldon
```

Port-forward

```
kubectl port-forward --address 0.0.0.0 svc/seldon-mesh -n seldon-mesh 9000:80
kubectl port-forward --address 0.0.0.0 svc/seldon-scheduler -n seldon-mesh 9004:9004
```

Simple test 

```
seldon model load -f seldon-examples/model-iris.yaml --scheduler-host 0.0.0.0:9004
seldon model infer iris '{"inputs": [{"name": "predict", "shape": [1, 4], "datatype": "FP32", "data": [[1, 2, 3, 4]]}]}' --inference-host 0.0.0.0:9000

seldon model load -f seldon-examples/tfsimple1.yaml --scheduler-host 0.0.0.0:9004
seldon model infer tfsimple1 --inference-host 0.0.0.0:9000 '{"inputs":[{"name":"INPUT0","data":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],"datatype":"INT32","shape":[1,16]},{"name":"INPUT1","data":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],"datatype":"INT32","shape":[1,16]}]}'
```

Simple drift 

https://docs.seldon.io/projects/seldon-core/en/v2/contents/examples/income.html

```
seldon model load -f seldon-examples/pipeline/income-preprocess.yaml --scheduler-host 0.0.0.0:9004
seldon model load -f seldon-examples/pipeline/income.yaml --scheduler-host 0.0.0.0:9004
seldon model load -f seldon-examples/pipeline/income-drift.yaml --scheduler-host 0.0.0.0:9004
seldon model load -f seldon-examples/pipeline/income-outlier.yaml --scheduler-host 0.0.0.0:9004
seldon pipeline load -f seldon-examples/pipeline/income-outlier.yaml --scheduler-host 0.0.0.0:9004
seldon pipeline list
```


## Seldon & Kserve

- https://docs.seldon.io/projects/seldon-core/en/latest/analytics/outlier_detection.html
- https://docs.seldon.io/projects/seldon-core/en/latest/analytics/drift_detection.html
