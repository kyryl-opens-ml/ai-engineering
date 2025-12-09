from google import genai
from google.genai import types
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from api.auth import get_current_user
from api.config import get_settings
from api.models.user import User

router = APIRouter()

SYSTEM_PROMPT = """You are a visualization expert. Analyze the uploaded PDF document and create a D3.js visualization that tells the story of the document's content.

Requirements:
1. Return ONLY valid JavaScript code that uses D3.js v7 (loaded via CDN)
2. The code should create a self-contained visualization
3. Use the variable `container` which is the DOM element to render into
4. The visualization should be informative and visually appealing
5. Include any necessary data extracted from the document inline in the code
6. Add appropriate labels, titles, and legends
7. Use a color scheme that works well on white background

Return only the JavaScript code, no markdown, no explanation."""


class AgentResponse(BaseModel):
    d3_code: str


@router.post("/visualize", response_model=AgentResponse)
async def visualize_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    pdf_bytes = await file.read()

    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=[
            types.Content(
                parts=[
                    types.Part(text=SYSTEM_PROMPT),
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="application/pdf",
                            data=pdf_bytes,
                        )
                    ),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low")
        ),
    )

    d3_code = response.text.strip()
    if d3_code.startswith("```"):
        lines = d3_code.split("\n")
        d3_code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    return AgentResponse(d3_code=d3_code)

