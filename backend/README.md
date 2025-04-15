# PRlyzer API

AI Pull Requests analyzer API

## Running
```
# install requirements
pip install -r requirements.txt
# run
fastapi run src/
```

## Endpoints

### 1. `GET /api/v1/login`
Redirects the user to GitHub for OAuth authentication.

---

### 2. `GET /api/v1/auth`
Handles the GitHub OAuth callback, validates the state and exchanges code for token.

**Query Parameters:**
- `code`: The authorization code returned from GitHub
- `state`: The state parameter to verify the session

---

### 3. `WS /api/v1/pull-requests`
WebSocket endpoint for analyzing pull requests.

**Send JSON Payload:**
```json
{
  "repo_name": "owner/repo",
  "pr_number": 123,
  "access_token": "github-access-token"
}
```
Server processes the PR and sends back analysis for each file via the WebSocket.

Client should keep the connection open to receive messages until it's closed by the server.

### response
```json
Success: 
{"filename": ..., "analysis": ...}

Errors:
{"error": "LLM API Quota/Rate limit"}
{"error": "Invalid PR number"}
{"error": "Invalid repo name or repo access issue"}
{"error": "Too big File size: {filename}, limit X Kb file size"}
{"error": "Too big file change in {filename}, limit Z lines per file"}
```