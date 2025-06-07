
# Module 1

![Container introduction](./../docs/into.jpg)

## Overview

This module introduces containerization and basic Kubernetes usage.
You'll learn how to build Docker images, push them to a registry and
deploy simple workloads on a local Kubernetes cluster.

## Practice

This module focuses on drafting your ML system design and containerizing a
simple application. You'll also create CI/CD pipelines and basic Kubernetes
manifests.

### Key tasks

- Draft a design document using the MLOps template.
- Build and push a Docker image.
- Set up GitHub Actions for CI/CD.
- Deploy your image to a local Kubernetes cluster.

***

# H1: Initial Design Draft

## Reading list:

- [Ml-design-docs](https://github.com/eugeneyan/ml-design-docs)
- [How to Write Design Docs for Machine Learning Systems](https://eugeneyan.com/writing/ml-design-docs/)
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [How Big Tech Runs Tech Projects and the Curious Absence of Scrum](https://newsletter.pragmaticengineer.com/p/project-management-in-tech)
- [Continuous Delivery for Machine Learning](https://martinfowler.com/articles/cd4ml.html)
- [Best practices for implementing machine learning on Google Cloud](https://cloud.google.com/architecture/ml-on-gcp-best-practices)
- [The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/aad9f93b86b7addfea4c419b9100c6cdd26cacea.pdf)
- [datascience-fails](https://github.com/xLaszlo/datascience-fails)
- [CS 329S Lecture 1. Machine Learning Systems in Production](https://docs.google.com/document/d/1C3dlLmFdYHJmACVkz99lSTUPF4XQbWb_Ah7mPE12Igo/edit#)
- [MLOps Infrastructure Stack](https://ml-ops.org/content/state-of-mlops)
- [You Don't Need a Bigger Boat](https://github.com/jacopotagliabue/you-dont-need-a-bigger-boat)
- [Why to Hire Machine Learning Engineers, Not Data Scientists](https://www.datarevenue.com/en-blog/hiring-machine-learning-engineers-instead-of-data-scientists)


## Task:

Write a design doc [example](https://docs.google.com/document/d/14YBYKgk-uSfjfwpKFlp_omgUq5hwMVazy_M965s_1KA/edit#heading=h.7nki9mck5t64) with the MLOps template from the [MLOps Infrastructure Stack doc](https://ml-ops.org/content/state-of-mlops) and for the next points (you can use an example from your work or make it up).
- Models in production.
- Pros/Cons of the architecture. 
- Scalability.
- Usability.
- Costs.
- Evolution.
- Next steps.
- ML Test score from this [article](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/aad9f93b86b7addfea4c419b9100c6cdd26cacea.pdf).
- Run over this design doc over [doc](https://github.com/xLaszlo/datascience-fails) and highlight all matches.
- Try to add business metrics into your design doc, [example](https://c3.ai/customers/ai-for-aircraft-readiness/).

## Criteria: 

- Approve / No approval.
- Notes: Repeat the same task at the end of the course for coursework.


# H2: Infrastructure

## Reading list:

- [0 to production-ready: a best-practices process for Docker packaging](https://www.youtube.com/watch?v=EC0CSevbt9k)
- [Docker and Python: making them play nicely and securely for Data Science and ML](https://www.youtube.com/watch?v=Jq68axbKIbg)
- [Docker introduction](https://docker-curriculum.com/)
- [Overview of Docker Hub](https://docs.docker.com/docker-hub/)
- [Introduction to GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Hello Minikube](https://kubernetes.io/docs/tutorials/hello-minikube/)
- [Kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Why data scientists shouldn’t need to know Kubernetes](https://huyenchip.com/2021/09/13/data-science-infrastructure.html)
- [Scaling Kubernetes to 7,500 nodes](https://openai.com/research/scaling-kubernetes-to-7500-nodes)
- [Course: CI/CD for Machine Learning (GitOps)](https://www.wandb.courses/courses/ci-cd-for-machine-learning)
- [Book: Kubernetes in Action](https://www.manning.com/books/kubernetes-in-action)

## Task:

- PR1: Write a dummy Dockerfile with a simple server and push it to your docker hub or github docker registry.
- PR2: Write CI/CD pipeline with github action that does this for each PR.
- PR3: Write YAML definition for Pod, Deployment, Service, and Job with your Docker image, Use minikube/kind for testing it.
- Install [k9s](https://k9scli.io/) tool.

## Criteria:

- 3 PRs are merged 
- CI/CD is green 

---

## Reference implementation

---

# H1: Initial Design Draft

[Google doc](https://docs.google.com/document/d/1mUAUVMdA6O3rxvjS87mm-tAisQXDQggRKEBv0nWPuP4/edit)

# H2: Infrastructure


# Docker

## Run hello-world

```bash
docker pull hello-world
docker run hello-world
```

Reference: https://hub.docker.com/_/hello-world

## Build and run

Build ml sample docker image

```bash
docker build --tag app-ml:latest ./app-ml
```

Run ml sample docker container

```bash
docker run -it --rm --name app-ml-test-run app-ml:latest
docker run -it --rm --name app-ml-test-run app-ml:latest python -c "import time; time.sleep(5); print(f'AUC = {0.0001}')"
```

Build web sample docker image

```bash
docker build --tag app-web:latest ./app-web
```

Build web sample docker image

```bash
docker run -it --rm -p 8080:8080 --name app-web-test-run app-web:latest
```

In a separate terminal, run the curl command to check access.

```bash
curl http://0.0.0.0:8080/
```

Bulti-build docker file, if you don't want to keep a lot of docker files.

```bash
docker build --tag app-web:latest --target app-web ./app-multi-build
docker build --tag app-ml:latest --target app-ml ./app-multi-build
```

## Share

Login to docker registry

```bash
export GITHUB_TOKEN=token
export GITHUB_USER=user
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin
```

Tag images

```bash
docker tag app-ml:latest ghcr.io/kyryl-opens-ml/app-ml:latest
docker tag app-web:latest ghcr.io/kyryl-opens-ml/app-web:latest
```

Push image

```bash
docker push ghcr.io/kyryl-opens-ml/app-ml:latest
docker push ghcr.io/kyryl-opens-ml/app-web:latest
```

## Registry

- [github](https://github.com/features/packages)
- [dockerhub](https://hub.docker.com/)
- [aws](https://aws.amazon.com/ecr/)
- [gcp](https://cloud.google.com/container-registry)

# CI/CD

Check code in this file

[CI example](./../.github/workflows/module-1.yaml)

## Providers

- [circleci](https://circleci.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Jenkins](https://www.jenkins.io/)
- [Travis CI](https://www.travis-ci.com/)
- [List of Continuous Integration services](https://github.com/ligurio/awesome-ci)

# Kubernetes

## Setup

Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

```bash
brew install kind
```

Create cluster

```bash
kind create cluster --name ml-in-production
```

Install kubectl

```bash
brew install kubectl
```

Check current context

```bash
kubectl config get-contexts
```

Install "htop" for k8s

```bash
brew install derailed/k9s/k9s
```

Run "htop" for k8s

```bash
k9s -A
```

## Use

Create pod for app-web

```bash
kubectl create -f k8s-resources/pod-app-web.yaml
```

Create pod for app-ml

```bash
kubectl create -f k8s-resources/pod-app-ml.yaml
```

Create job for app-ml

```bash
kubectl create -f k8s-resources/job-app-ml.yaml
```

Create deployment for app-web

```bash
kubectl create -f k8s-resources/deployment-app-web.yaml
```

To access use port-forwarding

```bash
kubectl port-forward svc/deployments-app-web 8080:8080
```

## Providers 

- [EKS](https://aws.amazon.com/eks/)
- [GKE](https://cloud.google.com/kubernetes-engine)
- [CloudRun](https://cloud.google.com/run)
- [AWS Fargate/ECS](https://aws.amazon.com/fargate/)


# Bonus

Sometimes Kubernetes might be overkill for your problem, for example, if you are a small team, it's a pet project, or you just don't want to deal with complex infrastructure setup. In this case, I would recommend checking out serverless offerings, some good examples of which I use all the time.

## Railway

- [Railway infrastructure platform](https://railway.app/) - nice too to deploy simple app.

```bash
open https://railway.app/
```

## Modal

- [The serverless platform for AI/ML/data teams](https://modal.com/) - nice too to deploy ML heavy app.

```bash
uv add modal
modal token new
uv run modal run -d ./modal-examples/modal_hello_world.py
uv run modal run -d ./modal-examples/modal_hello_world_training.py::function_calling_finetune
```
