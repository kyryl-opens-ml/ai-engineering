# Becoming an Agent Tech Lead!


## Motivation: 

I was a tech lead for a long time, and also built a roadmap for becoming one in https://kyrylai.com/2024/08/21/data-scientist-to-ml-tech-lead/. It's generally a good position - you can do more, deliver more, and own more. If you play your cards well, compensation comes with this automatically.

There are also many other amazing resources and books:

https://github.com/kuchin/awesome-cto
https://github.com/kdeldycke/awesome-engineering-team-management

The previous consensus was that you can grow to senior and stay at that level for a while in your career. Well - this is not true anymore. Now the default expectation is that you must become a tech lead, but maybe not for people - for AI agents for sure.

Luckily, when we are talking about technical leadership, there is a lot of commonality, so if you're getting better at one, it makes you better at another!


## Job explanation

At core you need to keep shit together! Whatever this means, for me it's usually:

- chat with product or act as product sometimes (however this is a different skillset)
- understand my team's strengths and weaknesses 
- have tech roadmap for short, mid and long term 
- architecture and tradeoff definitions
- establish eng culture: testing, style, planning 
- predictable delivery of sizable progress
- task slicing, defining expected outcome and assigning people

Many many more but simplified is: 

roadmap -> list of tasks -> sequence of execution -> steering teammates -> verification.

While keeping same level of tech culture and unblocking people where possible. 

Some tasks as tech lead you are going to do yourself, maybe most boring and unpleasant. 

Do you see where I am coming from? This is basically everyone's responsibility now. But instead of people you can use coding agents. And don't do tasks yourself but spend most time on verification and steering coding agents. 

## Example: 


I found it's hard to communicate ideas, but luckily - with LLMs I can build & show them at very marginal costs, so let's get real here and build shit! 

Let's solve: https://www.databricks.com/blog/introducing-officeqa-benchmark-end-to-end-grounded-reasoning 

Before I would probably think - looks interesting but nah, too much work, and busy with other stuff. But I have an on-demand team of super engineers (with some dementia but nobody is perfect), and I believe in my tech leading skills so let's cook it.


List of tasks: 

1. pull and setup storage for https://github.com/databricks/officeqa/tree/main
2. function to ingest files to file storage api 
3. file api for pdfs (v1)
4. file api for json (v2)
5. file api for transformed (v3)
6. evals for simple llm
7. evals for simple llm + rag (v1, v2, v3, and combinations)
8. dspy optimization
9. dspy evals 
10. llm finetuning for training data
11. llm finetuning eval
12. reporting and error analysis 




# Great idea #1

This is an amazing idea! 
POC & Concept: https://aistudio.google.com/u/3/apps/drive/1XMbAEaSgIg8q_PXH-RyRmHiVO9ztEWIc?pli=1&showAssistant=true&showPreview=true&resourceKey=


## One sentence: 
Kanban board to manage cloud coding agents from the same place. Or how I started loving playing games instead of fearing AI.

## Gameplan: 

1. Small post about the Agents SDK: DONE kyryl-truskovskyi_interesting-observation-i-noticed-most-coding-activity-7402890193491730432-HyQa
2. Choose only one agent & API: DONE Cursor https://cursor.com/docs/cloud-agent/api/endpoints#list-models, why - dogfooding.


Manual stage:
3. Electron project setup: DONE (see makefile) git commit -m "1. Electron project setup"
4. Script to do this manually: play: DONE
npx tsx scripts/cli.ts list github.com/kyryl-opens-ml/ai-engineering

5. Script to do this manually: actual workflow

npx tsx scripts/cli.ts start github.com/kyryl-opens-ml/ai-engineering
6. Script to do this manually: human handoff


Product mvp stage:
7. Column descriptions
[Backlog, Design, Build, Review]
8. Reproduce from Kanban view
9. Persistence

Let's plan together! 

I want to build a kanban board for my agents in my electron app: 

Backlog, Design, Build, Review, Done, Canceled

Backlog - column where I add tasks manually 
Design - column where I want to have a plan and ask Cursor for input on my task, concerns, etc 
Build - column where I want Cursor to actually start a coding agent and implement it. After done I want to see status of implementation and comment aka follow up if I don't like this. 
Review - column where I review outcome manually - aka wait for human input and verification. 
Done - I successfully integrated agent work into project - good example 
Canceled - I gave up on this agent and this is a failed case.


Each task should be editable - so I provide input and can add comments. Coding agent also outputs metadata there - so I can see URL and results. 

By default Design - just ask and don't implement 
By default Build - don't create PR 


Please add persistence layer - simple SQLite on file system would work. Also limit everything to one repo. Also have notion of projects or workspace. So flow is: 

I start new workspace and enter target repo: 
see empty columns: -> add tasks and start work, some tasks could be done by just agent, some tasks I have to do manually. 
and I can switch between different projects back and forth. 


Validations:

10. Projects
11. P1 ML in production
12. P2 Lienonme
13. P3 https://context-hosting.com/
14. P4 NoOCR
14. P5 Real Deal https://gemini.google.com/u/3/app/bcfe8279336d77da?pageId=none



Product delivery stage:
10. GitHub integrations
11. Testing
12. Blog post text
13. NPM desktop
14. NPM cloud


Gamifications stage:
15. Game descriptions - map with Kanban
16. Character for each
17. Animations for each
18. Testing & flow
https://aistudio.google.com/u/3/apps/drive/1AWeIyy7xHf1s7qJPExF-Fjfs-RQ__q2E?showAssistant=true&showPreview=true&resourceKey=
