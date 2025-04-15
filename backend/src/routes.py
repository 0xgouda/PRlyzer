from fastapi import APIRouter, HTTPException, status, WebSocket
from starlette.requests import Request
from src.config import oauth
from src.schemas import PullRequests
from os import getenv
from github import Github, GithubException
from itertools import islice
import google.generativeai as genai

# small limits to get the best out of AI
MAX_NUM_OF_FILES = 10
MAX_SIZE_OF_ORIGINAL_FILE = 4 * 1024 # 4 Kilo byte
MAX_CHANGED_LINES = 100

# configure Gemini AI
genai.configure(api_key=getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    return await oauth.github.authorize_redirect(request, getenv('CALLBACK_URL'))

@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 


# TODO: handle & add rate limiting
# TODO: fine-tune the model & prompts
@router.websocket("/pull-requests")
async def pull_request(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()

    try:
        PullRequests(**data)
    except:
        await websocket.send_json(f"Invalid Json Object: {data}")
        await websocket.close()
        return
        
    github = Github(login_or_token=data["access_token"])

    try:
        repo = github.get_repo(data["repo_name"], lazy=False)
    except GithubException as e:
        await websocket.send_json({"error": "Invalid repo name or repo access issue"})
        await websocket.close()
        return

    try:
        pr = repo.get_pull(data["pr_number"])
    except GithubException as e:
        await websocket.send_json({"error": "Invalid PR number"})
        return

    files = list(islice(pr.get_files(), MAX_NUM_OF_FILES))
    head_sha = pr.head.sha

    chat_session = model.start_chat()
    chat_session.send_message(f"My Repo Received A Pull Request with the following body {pr.body}, i am going to send you the files one by one to analyze them for any bugs, errors or incorrect implementations of the ideas provided in Pull Request Body")

    for file in files:
        filename = file.filename
        if file.additions + file.deletions > MAX_CHANGED_LINES:
            await websocket.send_json(f"Too big file change in {filename}")
            continue
        diffs = file.patch

        file_meta_data = repo.get_contents(filename, ref=head_sha)
        if file_meta_data.size > MAX_SIZE_OF_ORIGINAL_FILE:
            await websocket.send_json(f"Too big File: {filename}")
            continue
        content = file_meta_data.decoded_content

        response = chat_session.send_message(f"analyze the following diffs in the file named {filename} for any errors, bugs or incorrect implementations of the Pull Request Body, original file {content}, diffs {diffs}")
        await websocket.send_json({"fileName": filename, "response": response.text})
    await websocket.close()