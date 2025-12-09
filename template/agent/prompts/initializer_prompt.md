# Initializer Session

You are starting a NEW FastReact project. Your task is to analyze the app, set up configuration, and create a feature list.

## Step 1: Read the App Specification

Read `app_spec.md` to understand what the user wants to build.

## Step 2: Verify Modal Authentication (CRITICAL)

Before proceeding, verify Modal CLI is authenticated:

```bash
modal token show
```

**If NOT authenticated:**
1. Run `modal token new` to authenticate (opens browser)
2. If that fails, document in `claude-progress.txt` and warn the user
3. Do NOT proceed until Modal is authenticated

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

Read `app_spec.md` and identify what backend secrets are needed. Common patterns:
- AI/LLM features → `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- Database → `DATABASE_URL`
- Payments → `STRIPE_KEY`, `STRIPE_SECRET`
- Auth providers → `AUTH_SECRET`, OAuth credentials
- Email → `SENDGRID_API_KEY`, `RESEND_API_KEY`


## Step 5: Check Existing Modal Secrets

Check what secrets already exist:

```bash
modal secret list
```

Check if the project secret exists and what keys it contains:

```bash
modal secret list | grep <project-name>-secrets
```

## Step 6: Notify User of Required Configuration

Tell the user what they need to set up. Be specific about what's missing:

> **Configuration Required**
>
> Please complete the following before I can proceed:
>
> **1. Frontend Auth (`frontend/.env.local`):**
> - Go to https://modal.com/settings/proxy-auth-tokens
> - Create a new token
> - Fill in `VITE_MODAL_KEY` and `VITE_MODAL_SECRET`
>
> **2. Backend Secrets (Modal):**
> Your app requires these secrets. Create them at https://modal.com/secrets or via CLI:
> ```bash
> modal secret create <project-name>-secrets \
>   OPENAI_API_KEY="your-key" \
>   OTHER_SECRET="value"
> ```
>
> Required secrets:
> - `OPENAI_API_KEY`: For AI features
> - *(list others identified from app_spec.md)*
>
> Let me know when you've completed this setup.

**STOP HERE and wait for the user to confirm.**

## Step 7: Validate Configuration

After the user confirms:

### 7a. Validate Frontend Environment

```bash
cat frontend/.env.local
```

Verify `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` are not empty.

### 7b. Validate Modal Secrets Exist

```bash
modal secret list | grep <project-name>-secrets
```

If the secret doesn't exist or is missing required keys, ask the user to create it.

### 7c. Start Backend and Test

Start the backend:

```bash
cd backend && modal serve modal_app.py
```

Capture the URL from output (e.g., `https://workspace--project-backend-fastapi-app-dev.modal.run`)

Update `frontend/.env.local` with the URL:

```bash
sed -i 's|VITE_API_URL=.*|VITE_API_URL=<modal-url>|' frontend/.env.local
```

Test the connection with auth:

```bash
MODAL_KEY=$(grep VITE_MODAL_KEY frontend/.env.local | cut -d= -f2)
MODAL_SECRET=$(grep VITE_MODAL_SECRET frontend/.env.local | cut -d= -f2)

curl -H "Modal-Key: $MODAL_KEY" -H "Modal-Secret: $MODAL_SECRET" <modal-url>/api/health
```

If this returns `{"status": "ok"}`, configuration is complete. If you get a 401 error, ask the user to verify their proxy auth token values.

## Step 8: Set Up Puppeteer MCP for Browser Testing

Update `.mcp.json` to enable browser automation:

```json
{
  "mcpServers": {
    "puppeteer-mcp-claude": {
      "command": "npx",
      "args": ["-y", "puppeteer-mcp-claude", "serve"]
    }
  }
}
```

## Step 9: Install Frontend Dependencies

```bash
cd frontend && pnpm install && cd ..
```

## Step 10: Start Frontend and Verify

```bash
cd frontend && pnpm run dev
```

Frontend will be available at http://localhost:5173

Verify the connection works by checking the browser console for any errors.

## Step 11: Create feature_list.json

Based on the app description, create `feature_list.json` as a flat array:

```json
[
  {
    "category": "backend-api",
    "description": "What this feature does and why",
    "steps": ["Step 1 to verify", "Step 2 to verify", "Step 3 to verify"],
    "passes": false
  }
]
```

### Standard Categories for FastReact

- `backend-api` - FastAPI endpoints on Modal
- `frontend-ui` - React components and pages
- `state` - State management and data flow
- `auth` - Authentication and authorization
- `styling` - Tailwind/shadcn styling and responsive design
- `integration` - Frontend-backend integration

### Guidelines for Feature Breakdown

1. **Order by dependency**: Backend API first, then frontend integration
2. **One feature per session**: Each should be completable in ~20-30 min
3. **Specific verification steps**: Include exact UI actions to test
4. **15-30 features total**: Adjust based on app complexity
5. **All start with `"passes": false`**

### Required First Features

Always include these foundational features first:
1. Health check endpoint at `/api/health`
2. Root App component renders without errors
3. Frontend can connect to backend API (with auth)

## Step 12: Initial Commit

```bash
git add -A
git commit -m "Initialize project with feature_list.json and configuration"
```

## Step 13: Update Progress Notes

Write to `claude-progress.txt`:
- Modal authentication: Verified
- Proxy auth token: Configured and tested
- Modal secrets: <list what's configured>
- Summary of planned features
- Recommended implementation order

---

**IMPORTANT**: Do NOT implement any features yet. Just set up configuration and create the plan files.
