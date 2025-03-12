from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.src.database.main import init_db
from backend.src.applicants.routes import api_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app is starting")
    await init_db()
    yield
    print("app is shutting down")


app = FastAPI(
    title="Test service",
    version="0.1.0",
    description="A web test service for testing applicants",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
