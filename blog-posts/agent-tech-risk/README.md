## Agent for detecting structural technical risk

Localstack for data generation 
PyDantic for Agewnt

agent-tech-risk
## Intetion: 

Blog post +
  dataset on hf 
  agent 
  package 
  claude code 
  benchmark 
  text 
  structure 
  gpm
  ai sre


## structure 

1. Selling 
2. Tech
3. Selling

## Initial idea: 


I want to write a blog post on the topic "Agent for detecting structural technical risk" that would resonate with tech leaders at VC and PE firms.
Think of it as developing an agent application for technical due diligence of companies. 
But to avoid boiling the ocean - I would start simple: localstack + pydantic ai. 
One of the inspirations for this should be: https://deepmind.google/blog/introducing-codemender-an-ai-agent-for-code-security/ 

The stack I want to use: 

1. localstack 

Let's limit to AWS and GCP, Azure, other hyperscalers would follow. I don't want to create a bunch of AWS with structure problems as my evaluation framework. 
So I want to use localstack to generate "cases" aka dataset against which I would benchmark and test several agents. Dataset should be snapshot of AWS infra with known structure issues. 
Make sure cases resemble real life. Ideally visualization and explanation of the tech risk embedded into each would be useful. I could review and remove ones I don't like.
Do research on what are the most common tech risks in AWS infrastructure. 


2. pydantic ai 

Given my dataset via localstack. I want to develop an agent to find those issues. For now - just find, fix would come later. This agent should be a set of models, skills and MCP tools. I would prefer to use https://ai.pydantic.dev/#why-use-pydantic-ai and Gemini 3 as code LLM. 


As of now - let's work on a plan for dataset with localstack. Keep all code in blog-posts/agent-tech-risk folder please

I want it to be more sophisticated. Add cases about scalability, k8s issues, and more tech risks. Also, I want to generate them on the fly. Let's say we would have 10 tech risk categories [tr1, ..., tr10], and for each or combinations [tr1 + tr4] we could generate a case. Also, I want them to be realistic. Imagine companies which PE wants to buy - they might have dozens or hundreds of engineers and several AWS accounts.

## Tools 
https://github.com/NVIDIA-NeMo/DataDesigner?tab=readme-ov-file

