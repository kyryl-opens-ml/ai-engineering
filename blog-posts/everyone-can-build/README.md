# Everyone Should Build


![Everyone Should Build - Hero](images/blog-ecb-hero.png)


## TL;DR

- AI should write 100% of your code.
- Software engineering has a bright and exciting future.
- Build AI engineering strategy for your company.

## Shift! 

Confession: 

March 10, 2025 Dario Amodei of Anthropic said - "there in three to six months, where AI is writing 90% of the code" https://www.cfr.org/event/ceo-speaker-series-dario-amodei-anthropic I was skeptical, now - it's 100% for me and best engineering (and not only engineers). Typing code manually - never again, thanks! With next prediction "we might be 6-12 months away from models doing all of what software engineers do end-to-end" - as evidence shows - might be true as well! 


We have so many actual datapoints about how effective AI-enabled engineering has become, that it's impossible to ignore.


| Company | Claim | Source |
|---|---|---|
| Alan | 283 pull requests from non-engineers were shipped | [alan.com](https://alan.com/en/blog/discover-alan/a/everyone-can-build) |
| METR | AI capability on long tasks doubles roughly every 7 months | [metr.org (March 2025)](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) |
| Anthropic | Opus 4 and Opus 4.5 matching or outperforming take-home evaluation constraints | [Anthropic Engineering (January 2026)](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) |
| Anthropic | Opus 4.6 agent team built a 100,000-line C compiler capable of compiling the Linux kernel | [Anthropic Engineering (February 2026)](https://www.anthropic.com/engineering/building-c-compiler) |
| Spotify | Best developers haven't written a single line of code since December; shipped 50+ features in 2025 | [TechCrunch (February 2026)](https://techcrunch.com/2026/02/12/spotify-says-its-best-developers-havent-written-a-line-of-code-since-december-thanks-to-ai/) |

The shift is even bigger than when we moved from machine code to compilers!

![Compiler shift analogy](images/gh-1.png)

See this picture - well - we don't do this anymore!

If you have a good and well-defined task description - consider you have a solution.

But nothing speaks better than personal experience - just try it! Install Claude Code, Codex, Cursor - anything and build something!


Who Benefits Most

- Engineers: less time on repetitive implementation
- Prototypers/PM/Designers: faster idea-to-proof
- Operators who can steer and orchestrate agents

Core skill: ask clearly, instrument outputs, correct early.

## Coding Agent

Why does it happen? It's very easy to state this, but only few people understand the core of the reasoning: Agents. 

What Is an Agent (Practical Definition)

`Agent = LLM + Actions + Loop`

- `LLM`: reasoning and planning
- `Actions`: tools, shell, APIs, MCP, skills
- `Loop`: iterative execution until goal or stop condition

where if some of your actions are coding and executing code - you can call it a coding agent!

What Is an Agent (Intuitive Definition)

Imagine a simple process to process invoices for example - step 1 - step 2 - step 3 - it's small, it's predictable, and one size fits all solution. An agent solution for this use case can be a generated list of actions: 

![Business Process (static)](images/business-process.png)

but if any complications arise - the agent adapts: branching, adding steps, iterating as needed.

![Agent (dynamic)](images/agent-flow.gif)

For each input: the agent would realize exactly one unique instance of a simple business process, but it would be tailored to the specific input and circumstances. AKA from "one size fits all" to "tailor-made"


And what are the most successful agents out there? Coding! Because it's way easier to verify code (running or not, tests are passing or not, compiled or not, does software do what you want or not). Now images each agent might have it's own agent adn so on, it's areladt existsinsd [open exape: K2.5 Agent Swarm  https://www.kimi.com/blog/kimi-k2-5.html] [claude example: https://code.claude.com/docs/en/agent-teams] and works really good! 

## Future

So how does the future look and how to prepare yourself! Here are several of my predictions:

1. "agent tech leads"

Everyone becoemase agetn tech lead - aka agent orchestrator.

This is the future of software engineering: see new job description [https://github.com/kyryl-opens-ml/ai-engineering/blob/main/blog-posts/agent-tech-lead/JobDescription.md]. Product builder job would be to manage and support coding agents. Those who would be able to do it more efficiently would have more success.
![Agent tech lead](images/atl-1.png)

2. Make sure other agents are first class citizens of your product

Agent TAM > Humann TAM

There is a limited number of potential customers for your business, but there are unlimited numbers of agentic customers for the business. Exploding TAM by focusing on agents. You clearly are not going to build every single one, but you can become their provider for data, service, etc. [This is already haooneing](https://www.databricks.com/blog/databricks-neon). 


![Neon](images/db-1.png)


3. Generative UI

Structure product as data platform - your data layer is the base and moat. UI and presentation layer are going to be defined and written on demand and on the fly!

https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/


![Generative UI](images/gui-1.png)

4. Self-Driving SaaS

Software that run itself, setupf feedback loop process for your users and most of the contibutet would be done automaticall.

![Self-driving SaaS](images/linear-2.png)

5. Sandboxes as Infrastructure

thesis is very simpe 1x value -> 100x coding agents -> 100,000x sandbox executions

Examples:
- https://www.together.ai/code-sandbox
- https://modal.com/docs/guide/sandboxes
- https://www.daytona.io/
- https://e2b.dev/

The more efficient and secure your execution environment for coding agents - the faster the delivery!


## Strategy

As any business, you need to adapt and embrace this shift! My recommendation is to build a strategy from the get-go and rely on 3 simple tiers!


![3-tier path](images/blog-ecb-tiers-path.png)

1. `Tier 1: Prototype + Vision`

Make sure everyone uses AI coding for new work - prototyping, demos, POCs, visualization. Instead of writing PRDs etc - just build a demo and show how it would look like!

- Tools: AI Studio, Lovable, Bolt
- Goal: communicate product intent quickly
- Output: clickable prototype + feedback

Metric to track here: how many ideas you validated!

2. `Tier 2: More Impact`

Demos & validations are good - but you need to move AI engineering to converge into the core product - start using tools for your team, make sure they have access to a good amount of tokens.

- Tools: Claude Code, Codex, Gemini CLI, Cursor
- Requires: terminal, git workflow, deployment basics
- Output: real features with review pipeline

Metric to track here: development productivity!

3. `Tier 3: Direct Contribution`

This one is the most advanced, but gives you the most benefit - have a highway of AI-generated code into your application!

- Integrations: Slack, web app, task trackers, CI/CD
- Requires: verification, ownership model, guardrails
- Output: trusted agentic contribution in production

Metric to track here: customer metrics (time to solve bug, time to recovery, number of contributions by non-tech team)!

If you are planning to transform your company with AI-first coding, feel free to contact me to get help and set this up for your specific context!

Cheers!
