# Becoming an Agent Tech Lead!


## Motivation: 

I was a tech lead for a long time, and also built a roadmap for becoming one in https://kyrylai.com/2024/08/21/data-scientist-to-ml-tech-lead/. It's generally a good position - you can do more, deliver more, and own more. If you play your cards well, compensation comes with this automatically.

There are also many other amazing resources and books:

https://github.com/kuchin/awesome-cto
https://github.com/kdeldycke/awesome-engineering-team-management

The previous consensus was that you can grow to senior and stay at that level for a while in your career. Well - this is not true anymore. 

Now the default expectation is that you must become a tech lead, but maybe not for people - for AI agents for sure.

Luckily, when we are talking about technical leadership, there is a lot of commonality, so if you're getting better at one, it makes you better at another!


## Tech Lead Job

At core you need to keep shit together! Whatever this means, for me it's usually:

- chat with product or act as product sometimes (however this is a different skillset)
- understand my team's strengths and weaknesses 
- have tech roadmap for short, mid and long term 
- architecture and tradeoff definitions
- establish eng culture: testing, style, planning 
- predictable delivery of sizable progress
- task slicing, defining expected outcome and assigning people

Many many more but simplified is: 

roadmap/tech plan -> list of tasks -> sequence of execution -> steering teammates -> verification.

While keeping same level of tech culture and unblocking people where possible. 
Some tasks as tech lead you are going to do yourself, maybe most boring and unpleasant. 

## Meet your new subordinates! 

Do you see where I am coming from? This is basically everyone's responsibility now. But instead of people you are gping to use coding agents. And don't do tasks yourself but spend most time on verification and steering coding agents. 

Your new team is very good! It's a combination of LLM + Agent & Configuration on top of it. 
I used Cursor Cloud API [https://cursor.com/docs/cloud-agent/api/endpoints] for this blog post with the option to select from 5 LLMs. 

- claude-4.5-opus-high-thinking
- gpt-5.2
- gpt-5.2-high
- gemini-3-pro
- gemini-3-flash


As of now, publicly you can build this on top of Cursor Cloud API [https://cursor.com/docs/cloud-agent/api/endpoints] or Jules API [https://developers.google.com/jules/api]. 

I chose Cursor Cloud API because (a) I'm a heavy Cursor user (b) Cursor handles GitHub integration for me already. But there are many more options and they all at some point in time are going to have cloud API - OpenAI Codex, Claud Code, RooCode [https://roocode.com/] etc.


## Agent Tech Lead Job!

Techical side of your new job - is very simlar to usualy tech lead job - just need spend more time for setting right enginereirng course, since your subordinates are neven sleep, never tired and sometimes fails incredylbly! 

I wrote simpe descrtipt app to show how the future job would looks like: 


<img src="./docs/1.png" width="800"/>


We have the following columns: 

- Backlog - column to add big features / sizable chunk of work - think about it as something that would take you personally days 
- Design** - column I wish I would have, but I don't - I have built this on top of Cursor Cloud API and it does not have plan mode in cloud agent, but degeneracy will come there. 
- Build - column where Cursor actually starts a coding agent and implements it, this pulls conversation from actual cursors cloud agetn - and in sync with it. 

- Review - column where I review outcome manually - aka wait for human input and verification. main point - make this fast and stragirofkrwith end-to-end and integration tests.

- Done - I successfully integrated agent work into project - good example 
- Canceled - I gave up on this agent - bad example 

Critical to have Done & Canceled to have feedback loops for your coding agents.

- Human Takeover - something human must take over or required access granted. 


Each task is a separate agent and you can run hundreds of them in parallel.
And now your job is to: 

1. plan their work & global architecture 
2. handle corner cases & hard cases
3. make sure system is optimized for multiple agents: access, verification, sequence. 

For peactical example - you can try to import my "inegration test" for this lbog post - project to solve OfficeQA chellange.


## Future of job 

Long story shoudl - each engineerg if want to keep there job has to become agent tech lead. 
Code for the agent tech lead escrpt app is here: Fee free to modify and change it for your own need and our own unique workflows.

On funny notes software enginerring would become almost a strategy game! If you ever played warhammet, starscraf of rome totatl war: yoiu comapny become your map, your codign agents becoem unit and your job is to place them, unbload them and inverveate to local scale when someone get stacuk! 









## Similar project: 

https://github.com/eyaltoledano/claude-task-master



