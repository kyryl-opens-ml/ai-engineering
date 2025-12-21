# Becoming an Agent Tech Lead!


## Motivation: 

I was a tech lead for a long time, and also built a roadmap for becoming one in https://kyrylai.com/2024/08/21/data-scientist-to-ml-tech-lead/. It's generally a good position - you can do more, deliver more, and own more. If you play your cards well, compensation comes with this automatically.

There are also many other amazing resources and books:

https://github.com/kuchin/awesome-cto
https://github.com/kdeldycke/awesome-engineering-team-management

The previous consensus was that you can grow to senior and stay at that level for a while in your career. Well - this is not true anymore. 

Now the default expectation is that you must become a tech lead, but maybe not for people - for AI agents for sure.

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

## Getting real! 

So I wrote very minimalist agent managment kanban board! 


- desctribe process: from prompts 
- define example 
- show example 
- try it yourself! (npm install -g ..., npm run )
- show apis 
- how future is going to look like! 





## Integration test for it: 


Let's solve: https://www.databricks.com/blog/introducing-officeqa-benchmark-end-to-end-grounded-reasoning 

Before I would probably think - looks interesting but nah, too much work, and busy with other stuff. But I have an on-demand team of super engineers (with some dementia but nobody is perfect), and I believe in my tech leading skills so let's cook it.


List of tasks: 

1. pull and setup storage for https://github.com/databricks/officeqa/tree/main
I want to have a simple modal script to setup this repo https://github.com/databricks/officeqa/tree/main and pull all data

- keep all code in new folder under blog-posts
- write simple modal app to pull this repo and clone data to shared volume
- read modal creds from env vars


1.1 ingestions 

could you run actual ingestions from blog-posts/officeqa-setup, envs to do this should be in env var

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

## Similar project: 

https://github.com/eyaltoledano/claude-task-master




## Gameplan: 


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


So Cursor does not have planning mode in Cloud API, let's remove it altogether - go to build right away! (simpler)

Also some suggestions: 

- Design Agent: View in Cursor → I want it to open in browser not inside of app
- Design Agent: View in Cursor → I want to be able to copy it 
- don't store history - just pull it from agent and show agent responses too please 

## Validations:

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
