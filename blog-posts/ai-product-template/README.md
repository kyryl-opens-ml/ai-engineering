# AI Engineering Product Template

## TLDR: 

Meet the reusable and opinionated AI engineering-first product template—spin up multiple products and features from it, experiment in parallel, all while keeping your agents on the leash: https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template

![Alt text](./docs/3.png)


## Goal: 

There are several things I want to do:

- Build products fast
- Experiment with features
- Use multiple agents to work for me in parallel, for hours, days, weeks.
- Run 10/100/1000 coding agents in parallel without them stepping on each other's toes
- Go beyond "vibe-coded" POCs
- Actually run this in production

Aka have self-driving software That sounds wonderful and marketing promises me this, but empirical reality, however, says this is not possible yet (at least for me). Very quickly, your product can become a "hot mess."

So there are several principles I follow to make this possible:


Principles:

- Prioritize simplicity (always)
- Test, test, and test again. Integration tests and treat agent evaludation are first class citizen in any design.
- Focus on security.
- Implement guardrails.
- Perform rigorous verification for any change.
- Maintain a good overview of agents.

Long story short: From genrations to verificatiosn loop - sucess is good verifications I am confidenr about

![Alt text](./docs/1.png)

And company statengety view - verification at scale for multiple product, teams, agens, & features are main goal! Note down as one of the main resposnncit of teachnical leadership to do this.

![Alt text](./docs/2.png)

How do we starte with it? I my answer - Tempalte! 


## Template:

My current best answer - a custom template - is very slim, simple, testable, extensible and follow principlese I outlied above as much as possiable! 

Slim: Agents can now write any features, so you don't need much prebuilt stuff.
Simple: Even a full framework can make things complicated.
Testable: This is critical to prevent a hot mess.
Extensible: Especially extensible in a parallel way.



- Frontend: TypeScript + Vite for the UI: https://github.com/vitejs/vite
- Backend: Python + FastAPI for the API: https://github.com/fastapi
- CI/CD: GitHub Actions https://github.com/features/actions
- LLM: Gemini G3 (text, vision, live API, RAG) + DSPy for proper prompt optimization
- Auth: Supabase  https://github.com/supabase/supabase 
- Database: Postgres https://github.com/postgres/postgres
- Platform: Railway https://railway.app/
- ML: Modal https://modal.com/
- Orchestration: Dagster https://github.com/dagster-io/dagster
- Error Monitoring: Sentry https://github.com/getsentry/sentry
- LLM Monitoring & Evaluation: Braintrust https://braintrust.dev/


![Alt text](./docs/4.png)

A nice bonus to make it really "self-driving software" is that each tool has its own MCP server exposed to agents.




(MCP  https://github.com/github/github-mcp-server)
(MCP  https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
(MCP: https://supabase.com/docs/guides/getting-started/mcp)
(MCP: https://github.com/crystaldba/postgres-mcp)
(MCP: https://docs.railway.com/reference/mcp-server)
(MCP: https://github.com/kyryl-opens-ml/mcp-server-dagster)
(MCP: https://github.com/getsentry/sentry-mcp)
(MCP: https://www.braintrust.dev/docs/reference/mcp)



And most important—AI engineering first! What do I mean by this?


- Feature branches - each agents has it's own branch.
- Bulletproof testing & evaludations - CI/CD, custoemr criteris, end2end test each agent can run on demans.
- Each agent has its own cloud environment and can be verified independently
- Anyone can contribute to project: via Slack, Web, API, Custom UI, Editors.

Simple check for it: 
- could 10 agents can run in parallel and produce meaningful results? 
- Do you have evidencet to proce ai coding agent ouput ready to merge? 

In the case of an enterprise use case, your stack may be more complicated and vary widely, but the core principle—AI engineering first—still holds true in every case.
## Code 

It's here - give it a try! As a starting point I have very miniaml designad and two features as examples:

1. Agentic – the user uploads a PDF and the app generates the best visualization for it. Dynamic, non determnitic and artifacet is hard to manage / predict.

<table>
  <tr>
    <td><img src="./docs/a1.png" width="400"/></td>
    <td><img src="./docs/a2.png" width="400"/></td>
  </tr>
</table>

It has simple evaliations in form of integration tests; 

- does it works
- does it proeuce valdiate format
- does another llm thing it;s good! 
- does it perfoce well based on latberle data before.

2. Deterministic – simple CRUD on "items" (no AI), just boring stuff (which is hugely valuable).

<table>
  <tr>
    <td><img src="./docs/d1.png" width="400"/></td>
    <td><img src="./docs/d2.png" width="400"/></td>
  </tr>
</table>

CRUD for items - you've seen it before, and testing it is very straightforward: Arrange-Act-Assert pattern (https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/). This seems easy to add, but I swas multiple time (and hostenre guyily of this myself) - if you  miss to add it ad right time - cost of this - mgiht be very hight. 

Never undervalue this stage, and always ask agent to add integration tests and make sure to follow TDD!  

Both are important, and both are must-haves. 

- Feature branches - when you add new feature or build on top of Agentic feature & Deterministic feature - make sure agent has full avilait to have seprate envirments. 

Based on this you can add new feature in prappalr, on top of existing one or combinations. 


## Outcome: 

I am running a reality check of this template and contributing back my findings, opinions, and learnings. 
But so far, this is one of the best ways (at least for me) to ship 10x faster while staying in control! 
 
My main recommendation for engineering leaders—no matter your stack—is to empower AI engineering by defining a set of principles and strong verification mechanisms at the company strategy level, and making sure you are consistently following them.