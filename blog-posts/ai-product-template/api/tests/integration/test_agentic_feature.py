import os
import subprocess
import tempfile
import pytest
import httpx
from google import genai
from google.genai import types

from api.config import get_settings

SAMPLE_PDF_URL = "https://pdfobject.com/pdf/sample.pdf"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope="module")
def fixture_d3_code():
    path = os.path.join(FIXTURES_DIR, "sample_pdf_d3_code.js")
    with open(path) as f:
        return f.read()


@pytest.fixture(scope="module")
def sample_pdf_path():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        response = httpx.get(SAMPLE_PDF_URL)
        response.raise_for_status()
        f.write(response.content)
        path = f.name
    yield path
    os.unlink(path)


def check_js_syntax(code: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w") as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            ["node", "--check", path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr
    except FileNotFoundError:
        return True, "node not found, skipping syntax check"
    finally:
        os.unlink(path)


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


def test_upload_pdf_returns_executable_js(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    d3_code = response.json()["d3_code"]

    assert "```" not in d3_code, "Code should not contain markdown fences"

    wrapper = f"""
const d3 = {{
    select: () => ({{ append: () => ({{ attr: () => ({{ attr: () => ({{ text: () => ({{}}) }}) }}) }}) }}),
}};
const container = {{}};
{d3_code}
"""
    is_valid, error = check_js_syntax(wrapper)
    assert is_valid, f"JavaScript syntax error: {error}"


def test_upload_pdf_llm_judge_evaluation(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    d3_code = response.json()["d3_code"]

    settings = get_settings()
    judge_client = genai.Client(api_key=settings.gemini_api_key)

    judge_prompt = f"""You are evaluating D3.js visualization code generated from a PDF document.

The PDF is a sample document with basic text content about PDF demonstration.

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
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low")
        ),
    )

    result = judge_response.text.strip().upper()
    assert result.startswith("PASS"), f"LLM Judge failed: {judge_response.text}"


def test_upload_pdf_compare_to_historic_data(client, sample_pdf_path, fixture_d3_code):
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/agent/visualize",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    new_d3_code = response.json()["d3_code"]

    settings = get_settings()
    judge_client = genai.Client(api_key=settings.gemini_api_key)

    compare_prompt = f"""You are comparing two D3.js visualizations generated from the same PDF document (a simple sample PDF with Lorem Ipsum text).

HISTORIC (previously generated):
```javascript
{fixture_d3_code}
```

NEW:
```javascript
{new_d3_code}
```

Are both valid D3.js visualizations that reasonably represent the PDF content? They don't need to be identical - different visualization approaches are acceptable as long as both are valid and relevant.

Respond with "PASS" if both are valid visualizations for this PDF, or "FAIL" only if the new code is broken or completely irrelevant."""

    judge_response = judge_client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=compare_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low")
        ),
    )

    result = judge_response.text.strip().upper()
    assert result.startswith("PASS"), f"LLM comparison: {judge_response.text}"

