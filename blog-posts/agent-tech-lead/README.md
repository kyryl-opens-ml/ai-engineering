# Becoming an Agent Tech Lead!

## Motivation

I was a tech lead for a long time, and also built a roadmap for becoming one in [Data Scientist to ML Tech Lead](https://kyrylai.com/2024/08/21/data-scientist-to-ml-tech-lead/). It's generally a good position - you can do more, deliver more, and own more. If you play your cards well, compensation comes with this automatically.

There are also many other amazing resources and books:

- [awesome-cto](https://github.com/kuchin/awesome-cto)
- [awesome-engineering-team-management](https://github.com/kdeldycke/awesome-engineering-team-management)

The previous consensus was that you can grow to senior and stay at that level for a while in your career. Well - this is not true anymore. Now the default expectation is that you must become a tech lead, but maybe not for people - for AI agents for sure.

Luckily, when we are talking about technical leadership, there is a lot of commonality, so if you're getting better at one, it makes you better at another!

## Job Explanation

At core you need to keep shit together! Whatever this means, for me it's usually:

- Chat with product or act as product sometimes (however this is a different skillset)
- Understand my team's strengths and weaknesses 
- Have tech roadmap for short, mid and long term 
- Architecture and tradeoff definitions
- Establish eng culture: testing, style, planning 
- Predictable delivery of sizable progress
- Task slicing, defining expected outcome and assigning people

Many many more but simplified is: 

**roadmap -> list of tasks -> sequence of execution -> steering teammates -> verification**

While keeping same level of tech culture and unblocking people where possible. Some tasks as tech lead you are going to do yourself, maybe most boring and unpleasant. 

Do you see where I am coming from? This is basically everyone's responsibility now. But instead of people you can use coding agents. And don't do tasks yourself but spend most time on verification and steering coding agents. 

## Getting Real!

Let's translate these skills into practice. I'll use examples from my [ai-product-template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template) - a template I built specifically for agent-led development.

---

## 1. The Skill Translation Guide

Every tech lead skill has a direct equivalent when managing agents:

| Traditional Skill | For Humans | For Agents |
|-------------------|------------|------------|
| **Task Decomposition** | "Implement user auth" | "Add login endpoint with JWT, write 3 integration tests, update API docs" |
| **Quality Standards** | "Follow our style guide" | Integration tests + LLM judges + format validation |
| **Unblocking** | "Here's how the codebase works" | SYSTEM_PROMPT with context + MCP servers |
| **Progress Tracking** | Standups, Jira | Git branches, test results, CI status |
| **Code Review** | PR comments | Automated verification pipeline |

### The Key Difference: Specificity

Humans can ask clarifying questions. Agents make assumptions (usually wrong ones).

**Bad task for an agent:**
> "Build the authentication system"

**Good task for an agent:**
```
Add POST /auth/login endpoint that:
- Accepts {email, password} JSON body
- Returns {access_token, refresh_token} on success
- Returns 401 with {error: 'Invalid credentials'} on failure
- Write tests in tests/integration/test_auth.py
- Follow the patterns in test_deterministic_feature.py
```

Here's how I structure prompts in my template:

```python
SYSTEM_PROMPT = """You are a visualization expert. 
Analyze the uploaded PDF document and create a D3.js visualization.

Requirements:
1. Return ONLY valid JavaScript code that uses D3.js v7
2. The code should create a self-contained visualization
3. Use the variable `container` which is the DOM element to render into
4. Include any necessary data extracted from the document inline
5. Add appropriate labels, titles, and legends

Return only the JavaScript code, no markdown, no explanation."""
```

Notice: exact output format, explicit constraints, clear expectations. Just like scoping a well-defined ticket.

---

## 2. Your Agent-Ready Project Setup

Before agents can work effectively, your project needs the right infrastructure.

### AGENTS.md - The Agent's Instruction Manual

Every project should have an `AGENTS.md` file - think of it as onboarding documentation for agents:

```markdown
# AGENTS.md

## Run
- Start dev (backend + frontend): `make dev`
- Backend only: `make backend`
- Frontend only: `make frontend`

## Test
- API tests: `make run-test-api`
- UI tests: `make run-test-ui`

## Lint
- Lint all: `make lint`
- Format all: `make format`

## Database
- Run migrations: `make db-upgrade`
- Create migration: `make db-migrate`

## Deployment
- Each git branch gets its own isolated environment via Railway
```

### Makefile - Standardized Commands

Agents need predictable, repeatable commands. A Makefile provides exactly that:

```makefile
.PHONY: backend frontend dev run-test-api run-test-ui lint format

backend:
	@echo "Starting backend on http://localhost:8000..."
	cd api && PYTHONPATH=src uv run uvicorn api.main:app --reload --port 8000

frontend:
	@echo "Starting frontend on http://localhost:5173..."
	cd app && npm run dev

dev:
	@$(MAKE) -j 2 backend frontend

run-test-api:
	cd api && PYTHONPATH=src uv run pytest

run-test-ui:
	cd app && npm run test

lint:
	cd api && uv run ruff check src tests
	cd app && npm run lint

format:
	cd api && uv run ruff format src tests
	cd app && npm run lint -- --fix
```

### Test Infrastructure - Your Safety Net

The relationship between agent output and verification:

```
Agent generates code 
        ↓
   CI runs tests 
        ↓
    All pass? ──Yes──→ Ready for review
        ↓
       No
        ↓
 Agent gets feedback
        ↓
      Retry
```

This loop is your 1:1 with the agent. Tests are how you give feedback.

---

## 3. The Verification Pyramid

This is the core of agent tech leadership. You need multiple layers of verification:

```
                    ┌─────────────────────────┐
                    │   Historic Comparison   │  <- "Is it as good as before?"
                    ├─────────────────────────┤
                    │     LLM-as-Judge        │  <- "Does another AI approve?"
                    ├─────────────────────────┤
                    │   Format Validation     │  <- "Is the syntax correct?"
                    ├─────────────────────────┤
                    │    Basic Execution      │  <- "Does it run at all?"
                    └─────────────────────────┘
```

### Level 1: Does It Run?

The most basic check - did the agent produce something that executes?

```python
def test_upload_pdf_returns_valid_response(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "d3_code" in data
    assert isinstance(data["d3_code"], str)
    assert len(data["d3_code"]) > 50
```

### Level 2: Format Validation

Is the output in the expected format? Can it be parsed/executed?

```python
def test_upload_pdf_returns_executable_js(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    d3_code = response.json()["d3_code"]

    # Check it's not wrapped in markdown
    assert "```" not in d3_code, "Code should not contain markdown fences"

    # Validate JavaScript syntax
    wrapper = f"""
const d3 = {{
    select: () => ({{ append: () => ({{ attr: () => ({{}}) }}) }}),
}};
const container = {{}};
{d3_code}
"""
    is_valid, error = check_js_syntax(wrapper)
    assert is_valid, f"JavaScript syntax error: {error}"
```

### Level 3: LLM-as-Judge

Use another LLM to evaluate quality - especially useful for creative/generative outputs:

```python
def test_upload_pdf_llm_judge_evaluation(client, sample_pdf_path):
    # Get agent output
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )
    d3_code = response.json()["d3_code"]

    # Set up the judge
    settings = get_settings()
    judge_client = genai.Client(api_key=settings.gemini_api_key)

    judge_prompt = f"""You are evaluating D3.js visualization code.

The generated D3.js code is:
```javascript
{d3_code}
```

Evaluate if this code:
1. Is valid JavaScript that uses D3.js
2. Creates a meaningful visualization
3. Would render without errors in a browser

Respond with ONLY "PASS" or "FAIL" followed by a brief reason."""

    judge_response = judge_client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=judge_prompt,
    )

    result = judge_response.text.strip().upper()
    assert result.startswith("PASS"), f"LLM Judge failed: {judge_response.text}"
```

### Level 4: Historic Comparison

Compare against known-good outputs to catch regressions:

```python
def test_upload_pdf_compare_to_historic_data(client, sample_pdf_path, fixture_d3_code):
    # Get new output
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )
    new_d3_code = response.json()["d3_code"]

    # Compare against historic fixture
    settings = get_settings()
    judge_client = genai.Client(api_key=settings.gemini_api_key)

    compare_prompt = f"""Compare these two D3.js visualizations:

HISTORIC (previously approved):
```javascript
{fixture_d3_code}
```

NEW:
```javascript
{new_d3_code}
```

Are both valid D3.js visualizations? They don't need to be identical - 
different approaches are acceptable as long as both are valid.

Respond with "PASS" if both are valid, or "FAIL" if the new code is broken."""

    judge_response = judge_client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=compare_prompt,
    )

    result = judge_response.text.strip().upper()
    assert result.startswith("PASS"), f"Regression detected: {judge_response.text}"
```

---

## 4. Multi-Agent Workflow Example

Here's how to run multiple agents in parallel on a single feature.

### Scenario: Building a "User Dashboard" Feature

**Branch Strategy:**

```
main
 │
 ├── feature/dashboard-api    (Agent 1: Claude - Backend)
 │   └── Python endpoints + integration tests
 │
 ├── feature/dashboard-ui     (Agent 2: GPT-4 - Frontend)
 │   └── React components + unit tests
 │
 └── feature/dashboard-e2e    (Agent 3: Gemini - Testing)
     └── End-to-end tests + fixtures
```

### Step 1: Create Isolated Branches

```bash
git checkout -b feature/dashboard-api
git checkout -b feature/dashboard-ui  
git checkout -b feature/dashboard-e2e
```

### Step 2: Write Clear Task Specs

**For Claude (Backend API):**
```
Create /api/dashboard endpoints with user stats aggregation.

Requirements:
- GET /api/dashboard/stats - returns user activity metrics
- GET /api/dashboard/recent - returns last 10 items
- Both endpoints require authentication
- Write integration tests following test_deterministic_feature.py patterns
- Run `make run-test-api` to verify
```

**For GPT-4 (Frontend UI):**
```
Build Dashboard.tsx component that displays user stats.

Requirements:
- Fetch data from /api/dashboard/stats and /api/dashboard/recent
- Follow existing Sidebar.tsx component patterns
- Use existing CSS classes from App.css
- Write unit tests in Dashboard.test.tsx
- Run `make run-test-ui` to verify
```

**For Gemini (E2E Tests):**
```
Write end-to-end tests for the dashboard feature.

Requirements:
- Test full flow: login -> navigate to dashboard -> verify data displays
- Use Playwright for browser automation
- Create test fixtures for mock data
- Tests should work against Railway PR environment
```

### Step 3: Each Agent Gets Isolated Environment

With Railway PR environments:
- PR opens -> Railway deploys preview
- Each agent can test against real infrastructure
- No conflicts between agents

### Step 4: Merge Criteria

Before merging any agent's work:

- [ ] All tests pass (CI green)
- [ ] LLM judge approves (for agentic features)
- [ ] No regressions in existing tests
- [ ] Human spot-check on critical paths
- [ ] Code follows established patterns

---

## 5. Common Mistakes (and How to Avoid Them)

### Mistake 1: Merging Without Verification

> "The agent said it worked, so I merged it."

**Reality:** Agents are confident liars. They'll tell you everything is working while the code has obvious bugs.

**Fix:** Never merge without CI passing. Add this to your workflow:

```yaml
# .github/workflows/ci.yml
name: CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run API tests
        run: make run-test-api
      - name: Run UI tests
        run: make run-test-ui
      - name: Lint
        run: make lint
```

### Mistake 2: No Isolation Between Agents

> "I had three agents working on main branch..."

**Reality:** Agents will step on each other's toes, create merge conflicts, overwrite each other's work, and you'll spend more time fixing conflicts than reviewing code.

**Fix:** One agent = one branch = one environment.

```bash
# Each agent works in isolation
agent-1: feature/auth-backend
agent-2: feature/auth-frontend  
agent-3: feature/auth-tests

# Each gets its own Railway/Vercel/etc preview
```

### Mistake 3: Vague Task Definitions

> "Build the authentication system"

**Reality:** The agent will make 47 assumptions, 43 of which are wrong. You'll get a half-working OAuth implementation when you wanted simple JWT.

**Fix:** Be painfully specific:

```
BAD:  "Build authentication"

GOOD: "Add POST /auth/login endpoint that:
       - Accepts {email, password} JSON body
       - Validates email format and password length (min 8 chars)
       - Returns {access_token, refresh_token} on success
       - Returns 401 with {error: 'Invalid credentials'} on failure
       - access_token expires in 15 minutes
       - refresh_token expires in 7 days
       - Write tests in tests/integration/test_auth.py
       - Follow patterns from test_deterministic_feature.py"
```

### Mistake 4: Skipping Deterministic Tests

> "It's just CRUD, agents can't mess that up"

**Reality:** They absolutely can and will. Especially edge cases, authorization checks, and error handling.

**Fix:** Always include deterministic tests. These are your foundation:

```python
def test_item_access_denied_without_workspace_membership(db, user1, user2):
    client1 = UserClient(db, user1)
    client2 = UserClient(db, user2)

    # User1 creates a private workspace
    ws = client1.post("/workspaces/", json={"name": "Private"}).json()
    workspace_id = ws["id"]

    # User1 creates an item
    item = client1.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Secret", "description": "Private data"},
    ).json()

    # User2 should NOT be able to access it
    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 403

    resp = client2.get(f"/items/{item['id']}")
    assert resp.status_code == 403

    resp = client2.put(f"/items/{item['id']}", json={"title": "Hacked"})
    assert resp.status_code == 403

    resp = client2.delete(f"/items/{item['id']}")
    assert resp.status_code == 403
```

This test catches authorization bugs that agents frequently introduce.

---

## 6. Agent-Ready Checklist

Before you start running agents on your codebase, evaluate your project:

| # | Criterion | Why It Matters |
|---|-----------|----------------|
| 1 | **AGENTS.md exists** with clear run/test/lint commands | Agents need to know how to operate |
| 2 | **Makefile** provides standardized, repeatable commands | Consistent execution environment |
| 3 | **Integration tests** exist for core features | Catches regressions immediately |
| 4 | **CI/CD pipeline** runs on every PR | Automated verification gate |
| 5 | **PR environments** give each branch isolated testing | No agent interference |
| 6 | **LLM-as-Judge tests** for agentic features | Quality control for generative outputs |
| 7 | **Historic fixtures** for regression detection | Baseline for comparison |
| 8 | **Clear task templates** with expected inputs/outputs | Reduces agent assumptions |
| 9 | **Branch protection** prevents direct merges to main | Enforces verification workflow |
| 10 | **MCP servers** expose infrastructure to agents | Self-service for agents |

### Scoring

- **8-10 checks:** You're Agent Tech Lead ready. Start running parallel agents.
- **5-7 checks:** Getting there. Prioritize missing items before scaling.
- **0-4 checks:** Start with the [ai-product-template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template) and build up.

---

## Your Next Steps

1. **Clone the template:** [ai-product-template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template)

2. **Run through the checklist** and identify gaps in your current project

3. **Assign your first agent a well-scoped task** with clear verification criteria

4. **Watch the tests** - they're your new 1:1s with your agent team

5. **Iterate on your verification pyramid** - add more levels as you discover failure modes

The core insight: **From generations to verifications**. Your success as an Agent Tech Lead is directly proportional to the quality of your verification systems.

---

## Related Reading

- [AI Product Template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template) - The template this post is based on
- [Cursor Railway Vibe Coding PR Environments](https://kyrylai.com/2025/08/04/cursor-railway-vibe-coding-pr-environments/) - Deep dive on isolated agent environments
- [Build a Self-Healing K8s Agent with LibreChat MCP](https://kyrylai.com/2025/05/23/build-a-self-healing-k8s-agent-with-librechat-mcp/) - MCP server infrastructure
- [Dagster LLM Orchestration MCP Server](https://kyrylai.com/2025/04/09/dagster-llm-orchestration-mcp-server/) - Pipeline orchestration for agents
