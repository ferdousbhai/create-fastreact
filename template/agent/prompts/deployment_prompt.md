# Deployment Session

You are deploying a FastReact application to production.

## Step 1: Verify Ready

```bash
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'
cat frontend/.env.local
modal secret list | grep <project-name>-secrets
```

**Do NOT proceed if any features have `"passes": false`.**

## Step 2: Deploy Backend

```bash
cd backend && modal deploy modal_app.py
```

Capture the production URL (no `-dev` suffix): `https://<workspace>--<project>-backend-fastapi-app.modal.run`

## Step 3: Deploy Frontend to Cloudflare Pages

```bash
cd frontend
which wrangler || npm install -g wrangler
pnpm build
wrangler pages deploy dist --project-name=<project-name>
```

Or via Dashboard: Pages > Create project > Connect to Git (root: `frontend`, build: `pnpm build`, output: `dist`)

## Step 4: Set Cloudflare Environment Variables

In Dashboard > Pages > Project > Settings > Environment variables, add for Production:
- `VITE_API_URL` = `<modal-production-url>`
- `VITE_MODAL_KEY` and `VITE_MODAL_SECRET`

Then redeploy:
```bash
cd frontend && pnpm build && wrangler pages deploy dist --project-name=<project-name>
```

## Step 5: Verify Production

Open Cloudflare Pages URL, check DevTools Network tab:
- Requests go to Modal production URL (not dev)
- Responses are 200 (not 401 or CORS errors)

## Step 6: Document and Commit

Update `claude-progress.txt` with production URLs and deployment status.

```bash
git add -A && git commit -m "chore: production deployment complete"
```

---

## Troubleshooting

**401 Unauthorized:** Check `VITE_MODAL_KEY`/`VITE_MODAL_SECRET` in Cloudflare, verify token at https://modal.com/settings/proxy-auth-tokens

**Wrong API URL:** Check `VITE_API_URL` is production URL (no `-dev`), no trailing slash

**Build Failures:** Test `pnpm build` locally first, check Cloudflare build logs
