from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from src.config import oauth
from src.schemas import PullRequests
from os import getenv
from github import Github, GithubException

FILE_MAX_SIZE = 1024 * 1024 # 1 Mega byte

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

# TODO: limit size of added lines commits
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

    commits = pr.get_commits()

    for commit in commits:
        files = commit.files
        for file in files:
            filename = file.filename
            try:
                file_meta_data = repo.get_contents(filename, ref=commit.sha)
                if file_meta_data.size > FILE_MAX_SIZE:
                    print(f"Too big File: {filename}")
                    continue
                contents = file_meta_data.decoded_content
            except GithubException as e:
                print(f"Error fetching content of {filename}: {e}")
                continue

            added_content = file.patch

            print("filename ", filename)
            print("contents")
            print(contents)
            print("added_content")
            print(added_content)
