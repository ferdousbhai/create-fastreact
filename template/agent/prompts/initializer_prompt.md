# Initializer Session

You are starting a NEW FastReact project. Your task is to analyze the app, set up configuration, and create a feature list.

## Step 1: Read App Specification

Read `app_spec.md` to understand what the user wants to build.

## Step 2: Verify Modal Authentication

```bash
modal token show
```

If not authenticated, run `modal token new`. Do NOT proceed until authenticated.

## Step 3: Generate Frontend Environment File

Create `frontend/.env.local` with the required variables for the user to fill in:

```bash
cat > frontend/.env.local << 'EOF'
# =============================================================================
# REQUIRED: Fill in these values before continuing
# =============================================================================

# Modal Proxy Auth Token (REQUIRED)
# Create at: https://modal.com/settings/proxy-auth-tokens
# Click "Create new token" and copy both values below
VITE_MODAL_KEY=
VITE_MODAL_SECRET=

# Backend API URL (will be set automatically after modal serve)
VITE_API_URL=
EOF
```

## Step 4: Identify Required Backend Secrets

From `app_spec.md`, identify needed secrets (AI keys, database URLs, payment keys, etc.).

```bash
modal secret list | grep <project-name>-secrets
```

## Step 5: Notify User of Required Configuration

Tell the user to:
1. Fill in `frontend/.env.local` with proxy auth token from https://modal.com/settings/proxy-auth-tokens
2. Create Modal secrets: `modal secret create <project-name>-secrets KEY="value" ...`

List specific secrets needed based on `app_spec.md`. **STOP and wait for user confirmation.**

## Step 6: Validate and Start

After user confirms:

```bash
cat frontend/.env.local                    # Verify keys are filled
modal secret list | grep <project-name>    # Verify secret exists
cd backend && modal serve modal_app.py     # Start backend, note the URL
```

Update `VITE_API_URL` in `frontend/.env.local` with the Modal URL.

Test auth works:
```bash
curl -H "Modal-Key: $KEY" -H "Modal-Secret: $SECRET" <modal-url>/api/health
```

```bash
cd frontend && pnpm install && pnpm run dev
```

Verify at http://localhost:5173 - check console for errors.

## Step 7: Create feature_list.json

Create `feature_list.json` as a flat array:

```json
[
  {
    "category": "backend-api",
    "description": "What this feature does",
    "steps": ["Step 1 to verify", "Step 2 to verify"],
    "passes": false
  }
]
```

**Categories:** `backend-api`, `frontend-ui`, `state`, `auth`, `styling`, `integration`

**Guidelines:**
- Order by dependency (backend first, then frontend)
- Each feature completable in ~20-30 min
- 15-30 features total, all start with `"passes": false`
- Always start with: health check endpoint, App renders, frontend connects to backend

## Step 8: Commit and Document

```bash
git add -A && git commit -m "Initialize project with feature_list.json"
```

Update `claude-progress.txt` with: auth status, configured secrets, feature summary.

---

## ⚠️ SECURITY

**NEVER run backend code locally.** Always use `modal serve` or `modal deploy`.

**IMPORTANT**: Do NOT implement features yet - just configuration and planning.
