# AI Engineering Product Template

## TLDR: 

Many AI coding agents eventually devolve into chaos. This template is my attempt to stop that from happening.
[AI Product template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template)


<img src="./docs/3.png" width="800"/>


## Goal: 

We all want self-driving software, aka: 

- Build products fast
- Experiment with features
- Use multiple agents to work for me in parallel, for hours, days, weeks
- Run multiple agents in parallel on isolated feature branches with independent verification environments.
- Go beyond "vibe - coded" POCs
- Actually run this in production

Marketing promises this, but empirical reality says this is not possible yet (at least for me). Very quickly, your product can become a "hot mess."

So there are several principles I follow to make this possible:


Principles:

- Prioritize simplicity (always)
- Test, test, and test again. Integration tests and agent evaluation are first-class citizens in any design.
- Focus on security.
- Implement guardrails.
- Perform rigorous verification for any change.
- Maintain a good overview of agents.

Long story short: From generations to verifications loop - success is good verifications I am confident about.

<img src="./docs/1.png" width="800"/>

And company strategy view - verification at scale for multiple products, teams, agents, and features is the main goal! Note this down as one of the main responsibilities of technical leadership.

<img src="./docs/2.png" width="800"/>

How do we start with it? My answer - Template! 


## Template:

My current best answer - a custom template - is very feature-slim, simple, testable, extensible, and follows the principles I outlined above as much as possible! 

- Feature-slim: Agents can now write any features, so you don't need much prebuilt stuff.
- Simple/Managed Complexity: Rely on platforms like Railway and Modal to handle the heavy lifting.
- Testable: Integration tests are first-class citizens. (critical to prevent a hot mess)
- Extensible: Designed to run parallel feature branches seamlessly.


- Frontend: TypeScript + [Vite](https://github.com/vitejs/vite) for the UI
- Backend: Python + [FastAPI](https://github.com/fastapi) for the API
- CI/CD: [GitHub Actions](https://github.com/features/actions)
- LLM: Gemini 3 (text, vision, live API, RAG) + DSPy for proper prompt optimization
- Auth: [Supabase](https://github.com/supabase/supabase)
- Database: [Postgres](https://github.com/postgres/postgres)
- Platform: [Railway](https://railway.app/)
- ML: [Modal](https://modal.com/)
- Orchestration: [Dagster](https://github.com/dagster-io/dagster)
- Error Monitoring: [Sentry](https://github.com/getsentry/sentry)
- LLM Monitoring & Evaluation: [Braintrust](https://braintrust.dev/)


<img src="./docs/4.png" width="800"/>

A nice bonus to make it really "[self - driving software](https://linear.app/now/self-driving-saas)" is that each tool has its own MCP server exposed to agents. (Deep dive for infrastructure engineers: [Build a Self-Healing K8s Agent with LibreChat MCP](https://kyrylai.com/2025/05/23/build-a-self-healing-k8s-agent-with-librechat-mcp/))


- GitHub MCP: [Github MCP Server](https://github.com/github/github-mcp-server)
- GCP MCP: [GCP MCP Server](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- Supabase MCP: [Supabase MCP Server](https://supabase.com/docs/guides/getting-started/mcp)
- Postgres MCP: [Postgres MCP Server ](https://github.com/crystaldba/postgres-mcp)
- Railway MCP: [Railway MCP Server](https://docs.railway.com/reference/mcp-server)
- Dagster MCP: [Dagter MCP Server](https://github.com/kyryl-opens-ml/mcp-server-dagster) (deep dive about it: [Dagster LLM Orchestration MCP Server](https://kyrylai.com/2025/04/09/dagster-llm-orchestration-mcp-server/))
- Sentry MCP: [Sentry MCP Server](https://github.com/getsentry/sentry-mcp)
- Braintrust MCP: [Braintrust MCP Server](https://www.braintrust.dev/docs/reference/mcp)

By standardizing these tools via MCP, we don't just give the human a toolkit; we give the Agent a standardized interface to control the entire infrastructure.


And most important - AI engineering first! What do I mean by this?


- Feature branches - each agent has its own branch. (Deep dive: [Cursor Railway Vibe Coding PR Environments](https://kyrylai.com/2025/08/04/cursor-railway-vibe-coding-pr-environments/))
- Bulletproof testing and evaluations - CI/CD, customer criteria, end-to-end tests each agent can run on demand.
- Each agent has its own cloud environment and can be verified independently.
- Anyone can contribute to the project: via Slack, Web, API, Custom UI, Editors.

Simple check for it: 
- Could 10 agents run in parallel and produce meaningful results? 
- Do you have evidence to prove AI coding agent output is ready to merge? 

In the case of an enterprise use case, your stack may be more complicated and vary widely, but the core principle - AI engineering first - still holds true in every case.

## Code 

[Full code](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template) - give it a try! Spin up multiple products and features from it, experiment in parallel, all while keeping your agents on the leash. As a starting point, I have a very minimal design and two features as examples:

1. Agentic - the user uploads a PDF and the app generates the best visualization for it. The output is hard to predict or manage.

<table>
  <tr>
    <td><img src="./docs/a1.png" width="400"/></td>
    <td><img src="./docs/a2.png" width="400"/></td>
  </tr>
</table>

It has simple evaluations in the form of integration tests: 

- Does it work? ([test_upload_pdf_returns_valid_response](https://github.com/kyryl-opens-ml/ai-engineering/blob/main/blog-posts/ai-product-template/api/tests/integration/test_agentic_feature.py#L53))
- Does it produce a valid format? ([test_upload_pdf_returns_executable_js](https://github.com/kyryl-opens-ml/ai-engineering/blob/main/blog-posts/ai-product-template/api/tests/integration/test_agentic_feature.py#L67))
- Does another LLM think it's good? ([test_upload_pdf_llm_judge_evaluation](https://github.com/kyryl-opens-ml/ai-engineering/blob/main/blog-posts/ai-product-template/api/tests/integration/test_agentic_feature.py#L90))
- Does it perform well based on labeled data from before? ([test_upload_pdf_compare_to_historic_data](https://github.com/kyryl-opens-ml/ai-engineering/blob/main/blog-posts/ai-product-template/api/tests/integration/test_agentic_feature.py#L131))

Simplified code for the "Does another LLM think it's good?" part.

```python
def test_upload_pdf_llm_judge_evaluation(client, sample_pdf_path):
    """
    Integration Test: 
    1. Uploads a PDF to the Agent.
    2. Captures the generated visualization code.
    3. Uses a 'Judge' LLM (Gemini) to grade the output.
    """
    
    # 1. Act: Upload PDF and get the agent's response
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )
    
    assert response.status_code == 200
    generated_code = response.json()["d3_code"]

    # 2. Arrange: Set up the Judge
    judge_client = genai.Client(api_key=settings.gemini_api_key)
    
    judge_prompt = f"""
    You are an expert code reviewer.
    Evaluate this D3.js code generated from a PDF.
    
    Code:
    ```javascript
    {generated_code}
    ```
    
    Check for:
    1. Valid JavaScript syntax.
    2. Meaningful visualization logic.
    
    Respond with ONLY "PASS" or "FAIL" followed by a reason.
    """

    # 3. Assert: The Judge decides if the test passes
    judge_response = judge_client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=judge_prompt
    )

    result = judge_response.text.strip().upper()
    assert result.startswith("PASS"), f"LLM Judge rejected the code: {judge_response.text}"

```

2. Deterministic - simple CRUD on "items" (no AI), just boring stuff (which is hugely valuable).

<table>
  <tr>
    <td><img src="./docs/d1.png" width="400"/></td>
    <td><img src="./docs/d2.png" width="400"/></td>
  </tr>
</table>

[CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) for items - you've seen it before, and testing it is very straightforward: [Arrange-Act-Assert pattern](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/). This seems easy to add, but I saw multiple times (and honestly I'm guilty of this myself) - if you miss adding it at the right time, the cost of this might be very high. 

Never undervalue this stage, and always ask the agent to add integration tests and make sure to follow TDD!  

Both are important, and both are must-haves. 

- Feature branches - when you add a new feature or build on top of Agentic feature and Deterministic feature, make sure the agent has full availability to have separate environments. 

Based on this, you can add new features in parallel, on top of existing ones or combinations. 


## Outcome: 

I am stress-testing this template and contributing back my findings, opinions, and learnings. 
So far it's a my safety harness. It allows me to unleash 10 agents on a codebase knowing that if they mess up, the guardrails will catch them before production.
 
My main recommendation for engineering leaders - no matter your stack - is to empower AI engineering by defining a set of principles and strong verification mechanisms at the company strategy level, and making sure you are consistently following them.

