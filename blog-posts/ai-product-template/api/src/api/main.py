from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import items, workspaces, agent
from api.config import get_settings

app = FastAPI(title="Simple API")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
