from fastapi import FastAPI
from api.db.base import Base
from api.db.session import engine
from api.routes import items

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple API")

app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

