from fastapi import APIRouter, HTTPException, status, WebSocket
from starlette.requests import Request
from src.config import oauth
from src.schemas import PullRequests
from os import getenv
from github import Github, GithubException
import google.generativeai as genai

# configurable limits
MAX_NUM_OF_FILES = 5
MAX_SIZE_OF_ORIGINAL_FILE = 3 * 1024 # 3 Kilo byte
MAX_CHANGES_LINES_PER_FILE = 50

# configure Gemini AI
genai.configure(api_key=getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

router = APIRouter()

@router.get('/login')
async def github_login(request: Request):
    return await oauth.github.authorize_redirect(request, getenv('CALLBACK_URL'))

@router.get('/auth')
async def token_auth(request: Request) -> dict:
    try:
        token = await oauth.github.authorize_access_token(request)
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 


@router.websocket("/pull-requests")
async def pull_request(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()

    try:
        PullRequests(**data)
    except:
        await socketErr(websocket, f"Invalid Json Object: {data}")
        return
        
    github = Github(login_or_token=data["access_token"])

    try:
        repo = github.get_repo(data["repo_name"], lazy=False)
    except GithubException as e:
        await socketErr(websocket, "Invalid repo name or repo access issue")
        return

    try:
        pr = repo.get_pull(data["pr_number"])
    except GithubException as e:
        await socketErr(websocket, "Invalid PR number")
        return

    files = pr.get_files()[: MAX_NUM_OF_FILES]

    chat_session = model.start_chat()
    chat_session.send_message(f"My github Repo Received A Pull Request with the following body {pr.body}, i am going to send you the files one by one to analyze them for 1. bugs & edge cases 2. security issues 3. incorrect implementations of the ideas provided in Pull Request Body")

    for file in files:
        filename = file.filename
        if file.additions + file.deletions > MAX_CHANGES_LINES_PER_FILE:
            await websocket.send_json(f"Too big file change in {filename}, limit {MAX_CHANGES_LINES_PER_FILE} lines per file")
            continue

        file_meta_data = repo.get_contents(filename, ref=pr.head.sha)
        if file_meta_data.size > MAX_SIZE_OF_ORIGINAL_FILE:
            await websocket.send_json(f"Too big File size: {filename}, limit {MAX_SIZE_OF_ORIGINAL_FILE // 1024} Kb file size")
            continue
        content = file_meta_data.decoded_content

        try:
            response = chat_session.send_message(f"analyze the following diffs in the file named {filename} for 1. bugs & edge cases 2. security issues 3. incorrect implementations of the Pull Request Body provided before, make your answer precise, compact and relevant. original file ```{content}```, diffs ```{file.patch}```, ")
        except Exception as e:
            await socketErr(websocket, f"LLM API Quota/Rate limit")
            return
        await websocket.send_json({"fileName": filename, "analysis": response.text})
    await websocket.close()

async def socketErr(websocket: WebSocket, msg: str):
    await websocket.send_json({"error": msg})
    await websocket.close()