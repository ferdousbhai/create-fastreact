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

## Step 4: Deploy Frontend to Vercel

```bash
cd frontend

# Install Vercel CLI if needed
which vercel || pnpm add -g vercel

# Deploy
vercel --prod
```

Follow the prompts to link/create the Vercel project.

**Capture the Vercel URL** from output (e.g., `https://<project>.vercel.app`)

## Step 5: Configure Vercel Environment Variables

Read the auth values from `.env.local`:
```bash
cat frontend/.env.local
```

Set environment variables in Vercel:

```bash
cd frontend

# Set the production Modal backend URL
echo "<modal-production-url>" | vercel env add VITE_API_URL production

# Set auth credentials (read from .env.local)
echo "<vite-modal-key-value>" | vercel env add VITE_MODAL_KEY production
echo "<vite-modal-secret-value>" | vercel env add VITE_MODAL_SECRET production
```

## Step 6: Redeploy Frontend with Environment Variables

```bash
cd frontend && vercel --prod
```

## Step 7: Verify Production Deployment

Test the deployed application:

1. Open the Vercel URL in a browser
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

**Frontend (Vercel):**
- URL: https://<project>.vercel.app
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
- Frontend deployed to Vercel
- Environment variables configured
- Production URLs documented in claude-progress.txt"
```

---

## Troubleshooting

### 401 Unauthorized
- Verify `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` are set correctly in Vercel
- Verify the token is still valid at https://modal.com/settings/proxy-auth-tokens
- Redeploy frontend: `cd frontend && vercel --prod`

### API Calls to Wrong URL
- Check `VITE_API_URL` in Vercel environment variables
- Ensure it's the production URL (no `-dev` suffix)
- Ensure no trailing slash
- Redeploy frontend: `cd frontend && vercel --prod`
