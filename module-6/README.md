# Module 6

![Scaling and optimization](./../docs/serving.jpg)

## Overview

This module covers benchmarking, autoscaling and model optimization
techniques such as quantization.

## Practice

Benchmark and scale your model server, then explore optimization
techniques such as quantization.

### Key tasks

- Implement dynamic batching and ensembles.
- Benchmark REST and gRPC performance.
- Apply quantization or pruning.

***

# H11: Advanced features & benchmarking

## Reading list: 


- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Modal Web endpoints](https://modal.com/docs/guide/webhooks)
- [Deploy your side-projects at scale for basically nothing - Google Cloud Run](https://alexolivier.me/posts/deploy-container-stateless-cheap-google-cloud-run-serverless/)
- [K6 load tests](https://github.com/grafana/k6)
- [Locust load tests](https://github.com/locustio/locust)
- [Vegeta load tests](https://github.com/tsenart/vegeta)
- [About Simple gRPC benchmarking and load testing tool](https://github.com/bojand/ghz)
- [Most Effective Types of Performance Testing](https://loadninja.com/articles/performance-test-types/)
- [Reproducible Performance Metrics for LLM inference](https://www.anyscale.com/blog/reproducible-performance-metrics-for-llm-inference)
- [MLPerf Inference: Datacenter Benchmark Suite Results](https://mlcommons.org/benchmarks/inference-datacenter/)
- [MLPerf Inference Benchmark](https://arxiv.org/pdf/1911.02549.pdf)
- [ModelMesh Serving](https://kserve.github.io/website/master/modelserving/mms/modelmesh/overview/#learn-more)
- [Machine Learning Deployment: Shadow Mode](https://alexgude.com/blog/machine-learning-deployment-shadow-mode/)
- [Dynamic Batching](https://github.com/triton-inference-server/tutorials/tree/main/Conceptual_Guide/Part_2-improving_resource_utilization#what-is-dynamic-batching)
- [Model Ensembles](https://github.com/triton-inference-server/tutorials/tree/main/Conceptual_Guide/Part_5-Model_Ensembles)
- [HTTP/REST and GRPC Protocol](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/protocol/README.html)
- [Pipelines](https://docs.seldon.io/projects/seldon-core/en/v2/contents/pipelines/index.html)
- [3 Reasons Why Data Scientists Should Care About GRPC For Serving Models](https://bentoml.com/blog/3-reasons-for-grpc)


## Task:


- PR1: Write code for dynamic request batching for your model (you might use Triton, Seldon, or KServe for this).
- PR2: Write code for an ensemble of several models (you might use Triton, Seldon, or KServe for this).
- PR3: Write code for gRPC inference for your model server (you might use Triton, Seldon, or KServe for this).
- PR4: Write code for benchmarking your model server: report latency, RPS, etc.
- PR5: Write code for benchmarking your model server via REST and gRPC.
- PR6: Write code for benchmarking your model server by components: forward pass, data processing, network latency, etc.
- Update the Google doc about model inference performance and any advanced features you would need for your model.


## Criteria: 

- 6 PRs merged 
- Model inference performance in the google doc.


# H12: Scaling infra and model

## Reading list:

- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Introduction to streaming for data scientists](https://huyenchip.com/2022/08/03/stream-processing-for-data-scientists.html)
- [SageMaker Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)
- [Three Levels of ML Software](https://ml-ops.org/content/three-levels-of-ml-software)
- [Kubernetes Event-driven Autoscaling](https://keda.sh/)
- [REST vs Messaging for Microservices – Which One is Best?](https://solace.com/blog/experience-awesomeness-event-driven-microservices/)
- [End to end inference service example with Minio and Kafka](https://kserve.github.io/website/master/modelserving/kafka/kafka/)
- [Pending Request Count (Queue Size) Per-Model Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html)
- [Seldon and Kafka](https://docs.seldon.io/projects/seldon-core/en/v2/contents/architecture/index.html)
- [MTIA v1: Meta’s first-generation AI inference accelerator](https://ai.meta.com/blog/meta-training-inference-accelerator-AI-MTIA/)
- [Cloud TPU v5e Inference Converter introduction](https://cloud.google.com/tpu/docs/v5e-inference-converter)
- [AWS Inferentia](https://aws.amazon.com/blogs/aws/category/artificial-intelligence/aws-inferentia/)
- [All about AI Accelerators: GPU, TPU, Dataflow, Near-Memory, Optical, Neuromorphic & more](https://www.youtube.com/watch?v=VQoyypYTz2U)
- [The Top 23 Model Compression Open Source Projects](https://awesomeopensource.com/projects/model-compression)
- [FastFormers](https://github.com/microsoft/fastformers)
- [distil-whisper](https://github.com/huggingface/distil-whisper?tab=readme-ov-file)
- [S-LoRA: Serving Thousands of Concurrent LoRA Adapters](https://github.com/S-LoRA/S-LoRA?tab=readme-ov-file)
- [TensorFlow Model Optimization Toolkit — Pruning API](https://blog.tensorflow.org/2019/05/tf-model-optimization-toolkit-pruning-API.html)
- [SparseML](https://github.com/neuralmagic/sparseml)
- [Intel® Neural Compressor](https://github.com/intel/neural-compressor?tab=readme-ov-file)
- [Quantization](https://huggingface.co/docs/transformers/quantization)


## Task:

- PR1: Write code for using horizontal pod autoscaling for your pod with model server.
- PR2: Write code for async inference for your models with the help of queue (Kafka, or any other queue).
- PR3: Write code for optimize inference speed for your model with the help of pruning, distillation, and quatization.
- PR4: Write code for benchmarking your model after all optimization.
- Update the Google doc about model inference performance and any advanced features you would need for your model.

## Criteria:


- 4 PRs merged. 
- Model inference performance optimization in the google doc.

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


# Setup 


```
export WANDB_API_KEY='your key here'
kubectl create secret generic wandb --from-literal=WANDB_API_KEY=$WANDB_API_KEY
```


# Benchmarking

NOTE: **Premature optimization is the root of all evil!**

Deploy API from module 5

```
kubectl create -f ./k8s/app-fastapi.yaml
kubectl create -f ./k8s/app-triton.yaml
kubectl create -f ./k8s/app-streamlit.yaml
kubectl create -f ./k8s/kserve-inferenceserver.yaml
```

```
kubectl port-forward --address 0.0.0.0 svc/app-fastapi 8080:8080
kubectl port-forward --address 0.0.0.0 svc/app-streamlit 8080:8080
```

Run load test via locust

```
locust -f load-testing/locustfile.py --host=http://0.0.0.0:8080 --users 50 --spawn-rate 10 --autostart --run-time 600s
```

Run load test via k6

```
K6_WEB_DASHBOARD=true k6 run ./load-testing/load_test.js
```

Run on k8s 

```
kubectl create -f ./k8s/vegeta-job.yaml
```

- https://github.com/locustio/locust
- https://github.com/grafana/k6
- https://github.com/gatling/gatling
- https://ghz.sh/
- https://github.com/tsenart/vegeta


# Vertical scaling

- https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler
- https://docs.railway.app/reference/scaling 

# Horizontal scaling

- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

Install metric server 

```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

Update deployment 

```
kubectl apply -f k8s/app-fastapi-resources.yaml
```


Create from cli

```
kubectl autoscale deployment app-fastapi --cpu-percent=50 --min=1 --max=10
```

Create from yaml

```
kubectl create -f ./k8s/app-fastapi-hpa.yaml
```


- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/
- https://kserve.github.io/website/master/modelserving/autoscaling/autoscaling/


KNative autoscaling: https://kserve.github.io/website/master/modelserving/autoscaling/autoscaling/

```
kubectl create -f ./k8s/kserve-inferenceserver-autoscaling.yaml
```


```
seq 1 1000 | xargs -n1 -P10 -I {} curl -v -H "Host: custom-model-autoscaling.default.example.com" \
-H "Content-Type: application/json" \
"http://localhost:8080/v1/models/custom-model:predict" \
-d @data-samples/kserve-input.json
```

# Async inferece 


#### Simple example 

```
modal deploy ./queue/simple_queue.py
python queue/simple_queue.py
```

#### SQS example 

Setup SQS

```
git clone https://github.com/poundifdef/smoothmq.git
docker build -t sqs:latest ./smoothmq/
docker run -p 3000:3000 -p 3001:3001 sqs:latest 
```

Run web
```
export AWS_ACCESS_KEY_ID=DEV_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=DEV_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=us-east-1

python ./queue/sqs_queue.py run-api
```

Run worker

```
export AWS_ACCESS_KEY_ID=DEV_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=DEV_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=us-east-1

python ./queue/sqs_queue.py run-worker
```


Seldon V2 Examples: https://docs.seldon.io/projects/seldon-core/en/v2/contents/architecture/index.html
Kafka: https://kserve.github.io/website/master/modelserving/kafka/kafka/


## Model optimization


### Quatization 

- Hardware: EC2 g5.4xlarge (1 GPU A10, 16 vCPU, 64 GB RAM, $1.624 hour) [docs](https://aws.amazon.com/ec2/instance-types/g5/)
- Concurrent users: 100
- Data: https://huggingface.co/datasets/gretelai/synthetic_text_to_sql


| Approach   |   Median Response Time |   95% |   98% | F1
|:-----------|-----------------------:|------:|------:|
| default    |                   5600 |  6200 |  6300 |
| eetq       |                   5000 |  5700 |  5900 |
| fp8        |                   5000 |  5800 |  6000 |
| 4-bit-nf4  |                   8500 |  9200 |  9400 |
| 8-bit      |                  13000 | 14000 | 14000 |
| 4-bit-fp4  |                   8600 |  9300 |  9400 |

Add metrics & GPU unitization

```bash
docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/default.csv --html raw_data/default.html


docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct --quantize eetq
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/eetq.csv --html raw_data/eetq.html


docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct --quantize bitsandbytes 
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/8-bit.csv --html raw_data/8-bit.html


docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct --quantize bitsandbytes-fp4
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/4-bit-fp4.csv --html raw_data/4-bit-fp4.html


docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct --quantize bitsandbytes-nf4
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/4-bit-nf4.csv --html raw_data/4-bit-nf4.html


docker run --gpus all --shm-size 1g -p 8005:80 -v $PWD/data:/data ghcr.io/huggingface/text-generation-inference:2.3.0 --model-id microsoft/Phi-3.5-mini-instruct --quantize fp8
locust -f load_test.py -u 100 -r 10  --headless --run-time 5m --host=http://0.0.0.0:8005 --csv raw_data/fp8.csv --html raw_data/fp8.html
```


https://docs.vllm.ai/en/latest/quantization/supported_hardware.html
https://huggingface.co/docs/text-generation-inference/en/conceptual/quantization
https://www.adyen.com/knowledge-hub/llm-inference-at-scale-with-tgi


### Accelerators

https://modal.com/docs/examples/trtllm_llama


### Distillation

https://github.com/intel/neural-compressor/tree/master/examples/pytorch/nlp/huggingface_models/text-classification/distillation/eager

### Pruning

https://github.com/intel/neural-compressor/tree/master/examples/pytorch/nlp/huggingface_models/text-classification/pruning/eager



- https://github.com/huggingface/transformers/tree/main/examples/research_projects/distillation
- https://github.com/huggingface/distil-whisper/
- https://github.com/intel/neural-compressor
- https://github.com/neuralmagic/sparseml
- https://github.com/microsoft/fastformers

