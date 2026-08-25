# Emailsmith

Emailsmith is a local AI-assisted email composer. Describe the email you want in natural language, review the generated draft, and explicitly approve it before it is sent through Gmail. The backend uses FastAPI, Google OAuth, Gemini, LangGraph, PostgreSQL, and SQLite checkpointing; the frontend is a small static HTML/CSS/JavaScript client.

## Features

- Google OAuth sign-in with Gmail send permission
- Natural-language email drafting with Gemini
- Human approval step before delivery
- Gmail delivery through OAuth2 and SMTP
- LangGraph conversation state persisted in `checkpoints.sqlite`
- PostgreSQL tables for users and refresh-token metadata
- Static browser interface for drafting, editing, sending, and discarding messages


[Figma design link](https://www.figma.com/design/zYbQ8Mth6WoJhVWFGMHBd5/Untitled?node-id=6-31&t=TW7K5rbhCPBGZpv9-1)

## Requirements

- Python
- PostgreSQL running locally
- A Google Cloud project with OAuth 2.0 credentials
- A Gemini API key
- `uv` recommended for dependency and virtual-environment management
- VS Code Live Server, or another static server, for the frontend

## Setup

1. Create and activate a virtual environment:

	```powershell
	uv venv
	.\.venv\Scripts\Activate.ps1
	```

2. Install the project dependencies:

	```powershell
	uv sync
	```

3. Create a `.env` file in the repository root. Do not commit real credentials:

	```dotenv
	URL=postgresql+asyncpg://postgres:password@localhost/email_agent
	JWT_KEY=replace-with-a-long-random-value
	ALGORITHM=HS256
	REDIS_HOST=localhost
	REDIS_PORT=6379
	GMAIL_APP_PASSWORD=unused-by-current-oauth-flow
	GOOGLE_CLIENT_ID=your-google-client-id
	GOOGLE_CLIENT_SECRET=your-google-client-secret
	GOOGLE_REDIRECT_URL=http://127.0.0.1:8000/auth/google-auth/callback
	GEMINI_API_KEY=your-gemini-api-key
	```

	Create the `email_agent` PostgreSQL database before starting the API. The application creates its tables automatically at startup.

4. In Google Cloud Console, configure an OAuth consent screen and add this authorized redirect URI:

	`http://127.0.0.1:8000/auth/google-auth/callback`

	The application requests `openid`, `email`, `profile`, and Gmail send scopes. Use test users while the OAuth consent screen is in testing mode.

## Run the application

Start the API from the repository root:

```powershell
uv run uvicorn src.main:app --app-dir auth --reload --port 8000
```

Serve the frontend on port `5500` in a second terminal. With VS Code Live Server, open `frontend/home.html` and choose **Open with Live Server**. The current frontend is configured for:

`http://127.0.0.1:5500/frontend/home.html`

Open that URL in a browser, click **Sign in**, and grant the requested Google permissions.

## How it works

1. The frontend redirects the user to `/auth/google-auth/signup`.
2. Google redirects back to `/auth/google-auth/callback` after consent.
3. The backend stores or finds the user, sets HTTP-only `refresh_token` and `thread_id` cookies, and redirects to the frontend.
4. A prompt is sent to `POST /send_prompt`.
5. LangGraph asks Gemini to draft the email. If the prompt explicitly requests an email, the graph pauses for review and returns the proposed recipient, subject, and body.
6. **Send**, **Edit**, or **Discard** calls `POST /resume`. Only the send decision continues to Gmail delivery.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/auth/google-auth/signup` | Start Google OAuth |
| `GET` | `/auth/google-auth/callback` | Exchange the OAuth code and load Google profile data |
| `GET` | `/users/v1/google-authentication` | Create or find the user and establish browser cookies |
| `POST` | `/send_prompt` | Generate an email draft from `{ "email", "prompt" }` |
| `POST` | `/resume` | Approve or discard a draft |

FastAPI's interactive documentation is available at `http://127.0.0.1:8000/docs` while the API is running.

## Status

This repository is an early local prototype. There is no automated test suite or production deployment configuration yet.
