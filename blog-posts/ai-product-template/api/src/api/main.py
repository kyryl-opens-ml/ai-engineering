import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db.base import Base
from api.db.session import engine
from api.routes import items

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple API")

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

