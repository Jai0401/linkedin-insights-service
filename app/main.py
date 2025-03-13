# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.endpoints import pages

def create_tables():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables before application starts
    create_tables()
    yield
    # Shutdown: clean up resources if needed
    # This code runs when the application is shutting down

app = FastAPI(title="LinkedIn Insights Microservice", lifespan=lifespan)

app.include_router(pages.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)