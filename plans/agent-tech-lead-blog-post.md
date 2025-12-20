# Blog Post Plan: Becoming an Agent Tech Lead

## Overview

**Target Audience:** Engineers wanting to level up to tech lead through agent management  
**Outcome:** Readers can structure a project for agent-led development and run their first multi-agent workflow  
**Format:** Practical examples with code snippets from ai-product-template

---

## Blog Post Structure

### EXISTING INTRO (Keep as-is)
- Motivation and awesome resources links
- Job explanation: `roadmap -> tasks -> sequence -> steering -> verification`
- Core insight: Same skills, different "team members" (agents instead of people)

### GETTING REAL! (New Content to Add)

---

## Section 1: The Skill Translation Guide

Map traditional tech lead skills to agent management with practical examples.

| Traditional Skill | For Humans | For Agents | Practical Example |
|-------------------|------------|------------|-------------------|
| **Task Decomposition** | "Implement user auth" | "Add login endpoint with JWT, write 3 integration tests, update API docs" | Show how vague vs specific prompts yield different results |
| **Quality Standards** | "Follow our style guide" | Integration tests + LLM judges + format validation | Code from `test_agentic_feature.py` |
| **Unblocking** | "Here's how the codebase works" | SYSTEM_PROMPT with context + MCP servers | Code from `agent.py` |
| **Progress Tracking** | Standups, Jira | Git branches, test results, CI status | Railway PR environments |

### Code Example: Good Task Definition

```python
# From blog-posts/ai-product-template/api/src/api/routes/agent.py
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

**Key Point:** Notice how the prompt specifies exact output format, constraints, and expectations - just like a good tech lead would scope a ticket.

---

## Section 2: Your Agent-Ready Project Setup

### 2.1 AGENTS.md - The Agent's Instruction Manual

```markdown
# AGENTS.md

## Run
- Start dev: `make dev`
- Backend only: `make backend`

## Test
- API tests: `make run-test-api`
- UI tests: `make run-test-ui`

## Lint
- Lint all: `make lint`
- Format all: `make format`

## Deployment
- Each git branch gets its own isolated environment
```

**Key Point:** This file is your "onboarding doc" for agents. Keep it updated, keep it simple.

### 2.2 Makefile - Standardized Commands

Reference the Makefile from ai-product-template - agents need predictable, repeatable commands.

### 2.3 Test Infrastructure - Your Safety Net

Include diagram showing agent output -> CI tests -> feedback loop:

```
Agent generates code --> CI runs tests --> Pass? --> Ready for review
                                      --> Fail? --> Agent gets feedback --> Retry
```

---

## Section 3: The Verification Pyramid

### Visual Representation

```
                    ┌─────────────────────────┐
                    │   Historic Comparison   │  <- "Is it as good as before?"
                    │   test_compare_historic │
                    ├─────────────────────────┤
                    │     LLM-as-Judge        │  <- "Does another AI approve?"
                    │   test_llm_judge        │
                    ├─────────────────────────┤
                    │   Format Validation     │  <- "Is the syntax correct?"
                    │   test_executable_js    │
                    ├─────────────────────────┤
                    │    Basic Execution      │  <- "Does it run at all?"
                    │   test_valid_response   │
                    └─────────────────────────┘
```

### Level 1 - Does it run?

```python
def test_upload_pdf_returns_valid_response(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        response = client.post("/agent/visualize", files={"file": ("sample.pdf", f, "application/pdf")})
    
    assert response.status_code == 200
    assert "d3_code" in response.json()
    assert len(response.json()["d3_code"]) > 50
```

### Level 2 - Format Validation

```python
def test_upload_pdf_returns_executable_js(client, sample_pdf_path):
    # ... get response ...
    d3_code = response.json()["d3_code"]
    
    assert "```" not in d3_code, "Code should not contain markdown fences"
    is_valid, error = check_js_syntax(wrapper)
    assert is_valid, f"JavaScript syntax error: {error}"
```

### Level 3 - LLM-as-Judge

```python
def test_upload_pdf_llm_judge_evaluation(client, sample_pdf_path):
    # ... get agent output ...
    
    judge_prompt = f"""You are evaluating D3.js visualization code.
    Evaluate if this code:
    1. Is valid JavaScript that uses D3.js
    2. Creates a meaningful visualization
    3. Would render without errors
    
    Respond with ONLY "PASS" or "FAIL" followed by a reason."""
    
    result = judge_client.models.generate_content(model="gemini-3-pro-preview", contents=judge_prompt)
    assert result.text.strip().upper().startswith("PASS")
```

### Level 4 - Historic Comparison

```python
def test_upload_pdf_compare_to_historic_data(client, sample_pdf_path, fixture_d3_code):
    # Compare new output against known-good historical output
    compare_prompt = f"""Compare these two D3.js visualizations:
    
    HISTORIC: {fixture_d3_code}
    NEW: {new_d3_code}
    
    Are both valid visualizations? Respond PASS or FAIL."""
```

---

## Section 4: Multi-Agent Workflow Example

### Scenario: Building a "User Dashboard" Feature

**Branch Strategy Diagram:**

```
main
 ├── feature/dashboard-api    (Agent 1 - Claude: Backend endpoints + tests)
 ├── feature/dashboard-ui     (Agent 2 - GPT-4: React components + tests)
 └── feature/dashboard-e2e    (Agent 3 - Gemini: E2E tests + fixtures)
```

### Step-by-Step Process

**1. Create isolated branches**
```bash
git checkout -b feature/dashboard-api
git checkout -b feature/dashboard-ui  
git checkout -b feature/dashboard-e2e
```

**2. Write clear task specs for each agent**
- **Claude (API):** "Create /api/dashboard endpoints with user stats aggregation. Write integration tests following test_deterministic_feature.py patterns."
- **GPT-4 (UI):** "Build Dashboard.tsx component that fetches from /api/dashboard. Follow existing Sidebar.tsx patterns."
- **Gemini (E2E):** "Write end-to-end tests for the dashboard flow. Use Playwright."

**3. Each agent gets isolated Railway environment**
- PR opens -> Railway deploys preview
- Agent can test against real infrastructure

**4. Merge criteria (your verification)**
- All tests pass
- LLM judge approves (for agentic features)
- No regressions in existing tests
- Human spot-check on critical paths

---

## Section 5: Common Mistakes (and How to Avoid Them)

### Mistake 1: Merging Without Verification

> "The agent said it worked, so I merged it."

**Reality:** Agents are confident liars. Always run tests.

**Fix:** Never merge without CI passing:
```yaml
# .github/workflows/ci.yml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: make run-test-api
      - run: make run-test-ui
```

### Mistake 2: No Isolation Between Agents

> "I had three agents working on main branch..."

**Reality:** Agents will step on each other's toes, create conflicts, and blame each other.

**Fix:** One agent = one branch = one environment. Use Railway PR environments or similar.

### Mistake 3: Vague Task Definitions

> "Build the authentication system"

**Reality:** Agent will make 47 assumptions, 43 of which are wrong.

**Fix:** Be specific:
```
BAD:  "Build authentication"
GOOD: "Add POST /auth/login endpoint that:
       - Accepts {email, password} JSON body
       - Returns {access_token, refresh_token} on success
       - Returns 401 with {error: 'Invalid credentials'} on failure
       - Write tests in tests/integration/test_auth.py"
```

### Mistake 4: Skipping Deterministic Tests

> "It's just CRUD, agents can't mess that up"

**Reality:** They absolutely can and will. Especially edge cases.

**Fix:** Always include deterministic tests alongside agentic ones:
```python
def test_item_access_denied_without_workspace_membership(db, user1, user2):
    # User2 should NOT access User1's private workspace
    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 403
```

---

## Section 6: Agent-Ready Checklist

### Is Your Project Ready for Multi-Agent Development?

| # | Criterion | Check |
|---|-----------|-------|
| 1 | **AGENTS.md exists** with clear run/test/lint commands | ☐ |
| 2 | **Makefile** provides standardized, repeatable commands | ☐ |
| 3 | **Integration tests** exist for core features | ☐ |
| 4 | **CI/CD pipeline** runs on every PR | ☐ |
| 5 | **PR environments** give each branch isolated testing | ☐ |
| 6 | **LLM-as-Judge tests** validate agentic feature quality | ☐ |
| 7 | **Historic fixtures** enable regression detection | ☐ |
| 8 | **Clear task templates** define expected inputs/outputs | ☐ |
| 9 | **Branch protection** prevents direct merges to main | ☐ |
| 10 | **MCP servers** expose infrastructure to agents | ☐ |

### Scoring
- **8-10:** Agent Tech Lead ready
- **5-7:** Getting there, prioritize missing items
- **0-4:** Start with the template, build up from there

---

## Closing: Your Next Steps

1. Clone the [ai-product-template](https://github.com/kyryl-opens-ml/ai-engineering/tree/ai-product-template/blog-posts/ai-product-template)
2. Run through the checklist
3. Assign your first agent a well-scoped task
4. Watch the tests - they're your new 1:1s

---

## Implementation Notes

### Files to Create/Modify
- **New file:** `blog-posts/agent-tech-lead/README.md` - The complete blog post
- **Reference files:**
  - `blog-posts/ai-product-template/api/tests/integration/test_agentic_feature.py` - Verification pyramid examples
  - `blog-posts/ai-product-template/api/tests/integration/test_deterministic_feature.py` - CRUD test examples
  - `blog-posts/ai-product-template/api/src/api/routes/agent.py` - SYSTEM_PROMPT example
  - `blog-posts/ai-product-template/AGENTS.md` - Agent instruction file example
  - `blog-posts/ai-product-template/Makefile` - Standardized commands example

### Diagrams to Create
1. Skill translation table (can be markdown table)
2. Verification pyramid (ASCII art or image)
3. Multi-agent branch strategy (Mermaid diagram)
4. Agent feedback loop (flowchart)

### Code Snippets to Include
All code snippets are already in the ai-product-template - reference them directly or inline them in the blog post.
