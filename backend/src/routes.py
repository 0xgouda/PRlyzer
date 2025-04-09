from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request
from src.config import oauth
from os import getenv

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    return await oauth.github.authorize_redirect(request, getenv("CALLBACK_URL"))

@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 