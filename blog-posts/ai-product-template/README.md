# AI Engineering Product Template

## Goal: 

There are several things I want to do:

- Build products fast
- Experiment more
- Use multiple agents to work for me in parallel
- Use multiple agents to work for me in parallel for hours/days/weeks
- Run 10/100/1000 coding agents in parallel without them stepping on each other's toes
- Have self-driving software
- Go beyond "vibe-coded" POCs
- Actually run this in production

That sounds wonderful and marketing promises me this, but empirical reality, however, says this is not possible yet (at least for me). Very quickly, your product can become a "hot mess."

So there are several other principles I adopt to make this possible:

I would:

- Prioritize simplicity (always)
- Test, test, and test again
- Focus on security
- Implement guardrails
- Perform rigorous verification for any change
- Maintain a good overview of agents

Long story short: I want to accelerate by doing this via a set of verifiers.
How could I do this? Template.

## Template:

My current best answer—a custom template—is very slim, simple, testable, and extensible.

Slim: Agents can now write any features, so you don't need much prebuilt stuff.
Simple: Even a full framework can make things complicated.
Testable: This is critical to prevent a hot mess.
Extensible: Especially extensible in a parallel way.

The stack I chose for this is inspired by several recent implementations I like. A nice bonus to make it really self-serve is that each tool has its own MCP server exposed to agents.

- Frontend: TypeScript + Vite for the UI: https://github.com/vitejs/vite  (MCP: https://github.com/webfansplz/vite-plugin-vue-mcp)
- Backend: Python + FastAPI for the API: https://github.com/fastapi (MCP: https://github.com/tadata-org/fastapi_mcp)
- LLM: Gemini G3 (text, vision, live API, RAG)
- Auth: Supabase  https://github.com/supabase/supabase (MCP: https://supabase.com/docs/guides/getting-started/mcp)
- Database: Postgres https://github.com/postgres/postgres (MCP: https://github.com/crystaldba/postgres-mcp)
- Platform: Railway https://railway.app/ (MCP: https://docs.railway.com/reference/mcp-server)
- ML: Modal https://modal.com/ (MCP: https://modal.com/docs/examples/mcp_server_stateless)
- Orchestration: Dagster https://github.com/dagster-io/dagster (MCP: https://github.com/kyryl-opens-ml/mcp-server-dagster)
- Error Monitoring: Sentry https://github.com/getsentry/sentry (MCP: https://github.com/getsentry/sentry-mcp)
- LLM Monitoring: Braintrust

And most important—AI engineering first! What do I mean by this?

## AI engineering first

- Feature branches
- Bulletproof testing
- 10 agents can run in parallel and produce meaningful test results
- Each agent has its own cloud environment and can be verified independently
- Anyone can contribute to it: via Slack, web, API, custom UI, editors

## Code 

It's here: give it a try! As a starting point, I have 2 features:

- Agentic one – user uploads a CSV and the app generates the best visualization for it. This provides a "wow" effect to test.
- Deterministic one – simple CRUD on "items" (no AI), just boring stuff (which is hugely valuable).

Both are important, and both are must-haves. 


<Screenshot of agetic feature>

3 tests: works, valid foramt, valie informatl, valida based on data
no saving for now 
DSPy, etc etc 

<Screenshot of determinictic feature>

CRUD for items, you have see it before, and testing it's very stragforeard
https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/

## Outcome: 

I am running a reality check of this template and contributing back my findings, opinions, and learnings. 
So far, this is one of the best ways (for me) to ship 10x faster while staying in control! 
 



## Reference: 


https://developers.openai.com/codex/guides/build-ai-native-engineering-team/
https://linear.app/now/self-driving-saas
https://kyrylai.com/2025/08/04/cursor-railway-vibe-coding-pr-environments/
https://kyrylai.com/2025/07/28/vibe-coding-ml-team-case-study/


## TODO: 


1. Agent feature:
2. Determinitica feature

Keep only @ai-product-template context; everything else is irrelevant for this project.
Keep code simple and minimal, prioritizing maintainability and elegant solutions. The less code we have, the better we can support it.

I want you to implement the next feature:

- "Agent feature" instead Feature 1
- "Determinitica feature" instead Feature 2

Let's start with the Agent feature first:

- Allow users to upload a PDF in the UI.
- The UI sends the PDF to the backend.
- We process it using Document Understanding from Gemini (use the GEMINI_API_KEY environment variable).
- Gemini should generate D3.js code to visualize this PDF as a story.
- The UI displays this D3.js code in a sandbox, as the output could be anything.

Good! could you reanme it please

Agent – Agentic feature
Deterministic – Deterministic feature

in UI only please 

POC: 

- add Agent Feature intregraton test, there are shulbe be 3 tests: 
-- upload pdf and got good respose
-- upload pdf and evaludaiton of JS code is executable 
-- upload pdf and ask LLM as a Judge to evaluate if it solves the actualy problemt 
-- have pdf and resposne pre-generated -> upload same pdf again and compare resutls to oneeach other. 


Deterministic feature


This one is basic CRUD opetation on top of iterm! Just add UI to 

Create, read, update, and delete items for each user, with an option to share with other users.
3. Review with LLMs
4. Review with Ivanna 


## Prompt space



Let's plan first!


1. Auth features: 

1. Test for frontend + CI/CD to run them: DONE
2. Test for API + CI/CD to run them: DONE

3. Add auth with Supabase - make sure each user has it's own resourses 
6. Feature 1: Show how the API is connected
7. Feature 2: Some mock data
8. Docker-compose to run on-prem
9. Agentic feature + tests for it from API + UI
Agentic feature - let's use 
10. Settings page for user with placeholders


## History: 

git commit -m "0. init app"
git commit -m "1. api"
git commit -m "2. connect api and app"
git commit -m "3. sidebar"
git commit -m "4. add api"
git commit -m "5. feature branches"
git commit -m "6. auth"
git commit -m "7. base text"
git commit -m "8. agent feature"


git push origin ai-product-template
