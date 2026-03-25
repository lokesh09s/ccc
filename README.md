# Srihari Chatbot — Google Cloud Run Deployment

## Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install
- Docker installed (only needed if building locally)

---

## Step 1 — Set up your project

```bash
gcloud auth login
gcloud projects create srihari-chat --name="Srihari Chat"
gcloud config set project srihari-chat
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

---

## Step 2 — Put your files in one folder

```
srihari_app/
├── app.py
├── requirements.txt
├── Dockerfile
└── srihari.jpg   ← drop your image file here (any of the supported names)
```

---

## Step 3 — Deploy directly from source (no Docker needed locally)

```bash
cd srihari_app

gcloud run deploy srihari-chat \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY_HERE",SRIHARI_PASSWORD="srihari" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

Replace `sk-or-v1-YOUR_KEY_HERE` with your actual OpenRouter API key.

Cloud Build will build the Docker image, push it to Artifact Registry, and deploy it.
It takes ~3-5 minutes. At the end you get a URL like:
`https://srihari-chat-xxxxxxxxxx-uc.a.run.app`

---

## Step 4 — Custom domain (optional)

In Cloud Console → Cloud Run → your service → Custom Domains → Add mapping.
Or use a free subdomain via Cloudflare if you own a domain.

---

## Environment variables

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `SRIHARI_PASSWORD` | Login password (default: `srihari`) |

Never put the API key directly in code. The app reads it from env vars.

---

## How the session isolation works

- Each browser tab gets a unique UUID in `st.session_state` on first load
- Chat history is stored **only** in `st.session_state` (in-memory)
- When the browser tab closes, the session dies, chat is gone
- Two people with the same name get different `session_id` values → completely separate chats
- No database, no file persistence

---

## Updating the app

```bash
gcloud run deploy srihari-chat --source .
```

Same command, it redeploys with the latest code.

---

## Estimated cost

Cloud Run has a generous free tier:
- 2 million requests/month free
- 360,000 GB-seconds compute free

For a small chatbot with occasional use: **effectively free** unless it goes viral.
Set a budget alert at $5 in Cloud Console just in case.
