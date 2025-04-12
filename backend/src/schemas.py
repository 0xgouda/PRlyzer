from pydantic import BaseModel

class PullRequests(BaseModel):
    repo_name: str
    pr_number: int
    access_token: str