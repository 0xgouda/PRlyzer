from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request
from src.config import oauth
from src.schemas import PullRequests
from os import getenv
from github import Github, GithubException
from itertools import islice

# small limits to get the best out of AI
MAX_NUM_OF_FILES = 10
MAX_SIZE_OF_ORIGINAL_FILE = 4 * 1024 # 4 Kilo byte
MAX_CHANGED_LINES = 100

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

# TODO: return size errors to user
@router.post('/pull-requests')
def pull_request(data: PullRequests):
    github = Github(login_or_token=data.access_token)

    try:
        repo = github.get_repo(data.repo_name, lazy=False)
    except GithubException as e:
        return {"error": "Invalid repo name or repo access issue"}

    try:
        pr = repo.get_pull(data.pr_number)
    except GithubException as e:
        return {"error": "Invalid PR number"}

    pr_body = pr.body
    files = list(islice(pr.get_files(), MAX_NUM_OF_FILES))
    head_sha = pr.head.sha

    for file in files:
        filename = file.filename
        if file.additions + file.deletions > MAX_CHANGED_LINES:
            print(f"Too big file change")
            continue
        diffs = file.patch

        file_meta_data = repo.get_contents(filename, ref=head_sha)
        if file_meta_data.size > MAX_SIZE_OF_ORIGINAL_FILE:
            print(f"Too big File: {filename}")
            continue
        content = file_meta_data.decoded_content

        analyze(filename, diffs, content, pr_body) 

# TODO: connect to the LLM API to analyze
def analyze(filename, diffs, content, pr_body):
    pass
