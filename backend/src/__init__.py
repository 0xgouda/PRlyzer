from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from src.routes import router
from starlette.middleware.sessions import SessionMiddleware
from os import getenv

version = "v1"

app = FastAPI(
    title="PRlyzer",
    description="AI Pull Requests Analyzer",
    version=version,
)

app.add_middleware(SessionMiddleware, secret_key=getenv("SECRET_KEY"))
app.include_router(router=router, prefix=f"/api/{version}")