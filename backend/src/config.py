from authlib.integrations.starlette_client import OAuth
from os import getenv

oauth = OAuth()
oauth.register(
    name="github",
    client_id=getenv("GITHUB_CLIENT_ID"),
    client_secret=getenv("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "repo"},
)