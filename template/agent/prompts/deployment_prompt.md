# Deployment Session

You are deploying a FastReact application to production. All configuration was collected during initialization, so deployment is automated.

## Step 1: Verify App is Ready

```bash
# Check all features pass
echo "Passing: $(cat feature_list.json | grep -c '"passes": true')"
echo "Failing: $(cat feature_list.json | grep -c '"passes": false')"
```

**Do NOT proceed if any features have `"passes": false`.** Go back and fix them first.

## Step 2: Verify Configuration

Check that all required configuration exists:

```bash
# Check frontend has auth configured
cat frontend/.env.local
```

Should contain:
- `VITE_API_URL` (will be updated to production URL)
- `VITE_MODAL_KEY`
- `VITE_MODAL_SECRET`

```bash
# Check Modal secret exists
modal secret list | grep <project-name>-secrets
```

## Step 3: Deploy Backend to Modal

```bash
cd backend && modal deploy modal_app.py
```

**Capture the production URL** from output. It will look like:
```
https://<workspace>--<project>-backend-fastapi-app.modal.run
```

(Note: Production URL does NOT have `-dev` suffix)

## Step 4: Deploy Frontend to Cloudflare Pages

### Option A: Via Wrangler CLI

```bash
cd frontend

# Install Wrangler CLI if needed
which wrangler || npm install -g wrangler

# Build the frontend
pnpm build

# Deploy to Cloudflare Pages
wrangler pages deploy dist --project-name=<project-name>
```

Follow the prompts to log in (if needed) and create/link the Cloudflare Pages project.

### Option B: Via Cloudflare Dashboard

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) > Pages
2. Click "Create a project" > "Connect to Git"
3. Select your repository
4. Configure build settings:
   - **Root directory**: `frontend`
   - **Build command**: `pnpm build`
   - **Build output directory**: `dist`
5. Click "Save and Deploy"

**Capture the Cloudflare Pages URL** from output (e.g., `https://<project>.pages.dev`)

## Step 5: Configure Cloudflare Pages Environment Variables

Set environment variables in Cloudflare Pages:

### Via Dashboard (Recommended)
1. Go to Cloudflare Dashboard > Pages > Your project > Settings > Environment variables
2. Add the following for **Production**:
   - `VITE_API_URL` = `<modal-production-url>`
   - `VITE_MODAL_KEY` = `<vite-modal-key-value>`
   - `VITE_MODAL_SECRET` = `<vite-modal-secret-value>`
3. Click "Save"

### Via Wrangler CLI
```bash
cd frontend

# Set production environment variables
wrangler pages secret put VITE_API_URL --project-name=<project-name>
# Enter: <modal-production-url>

wrangler pages secret put VITE_MODAL_KEY --project-name=<project-name>
# Enter: <vite-modal-key-value>

wrangler pages secret put VITE_MODAL_SECRET --project-name=<project-name>
# Enter: <vite-modal-secret-value>
```

## Step 6: Redeploy Frontend with Environment Variables

```bash
cd frontend && pnpm build && wrangler pages deploy dist --project-name=<project-name>
```

Or trigger a new deployment from the Cloudflare Dashboard.

## Step 7: Verify Production Deployment

Test the deployed application:

1. Open the Cloudflare Pages URL in a browser
2. Open browser DevTools → Network tab
3. Perform actions that trigger API calls
4. Verify:
   - Requests go to the Modal production URL (not dev URL)
   - Responses are `200 OK` (not `401` or CORS errors)
   - App functions correctly

## Step 8: Update Progress Notes

Append to `claude-progress.txt`:

```
### Production Deployment - [Date]

**Backend (Modal):**
- URL: https://<workspace>--<project>-backend-fastapi-app.modal.run
- Status: Deployed

**Frontend (Cloudflare Pages):**
- URL: https://<project>.pages.dev
- Environment variables: Configured

**Deployment Status:** Complete

**Verification:**
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] API calls succeed with authentication
- [ ] Core user flows work in production
```

## Step 9: Final Commit

```bash
git add -A
git commit -m "chore: production deployment complete

- Backend deployed to Modal
- Frontend deployed to Cloudflare Pages
- Environment variables configured
- Production URLs documented in claude-progress.txt"
```

---

## Troubleshooting

### 401 Unauthorized
- Verify `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` are set correctly in Cloudflare Pages
- Verify the token is still valid at https://modal.com/settings/proxy-auth-tokens
- Redeploy frontend after updating environment variables

### API Calls to Wrong URL
- Check `VITE_API_URL` in Cloudflare Pages environment variables
- Ensure it's the production URL (no `-dev` suffix)
- Ensure no trailing slash
- Redeploy frontend after updating environment variables

### Build Failures
- Ensure `pnpm build` works locally before deploying
- Check Cloudflare Pages build logs for errors
- Verify Node.js version compatibility (set `NODE_VERSION` env var if needed)
