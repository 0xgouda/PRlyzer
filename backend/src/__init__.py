from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import router
from starlette.middleware.sessions import SessionMiddleware
from os import getenv

version = "v1"

app = FastAPI(
    title="PRlyzer",
    description="AI Pull Requests Analyzer",
    version=version,
)

origins = [
    "http://localhost:4000"
]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["GET"],
)

app.add_middleware(SessionMiddleware, secret_key=getenv("SECRET_KEY"))
app.include_router(router=router, prefix=f"/api/{version}")