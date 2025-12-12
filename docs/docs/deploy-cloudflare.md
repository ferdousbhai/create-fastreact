# Deploy Frontend to Cloudflare Pages

Get your FastReact frontend live on the edge in under 5 minutes.

Cloudflare Pages is a JAMstack platform for deploying frontend applications. It provides:

- **Global edge network** - Your app loads fast everywhere
- **Automatic HTTPS** - SSL certificates handled for you
- **Preview deployments** - Every git branch gets its own URL
- **Zero configuration** - Vite projects work out of the box

## Prerequisites

- A FastReact project (run `pnpm create fastreact my-app` if you haven't)
- A [Cloudflare account](https://dash.cloudflare.com/sign-up) (free tier works great)
- Your code pushed to GitHub or GitLab

## Option 1: Deploy via Cloudflare Dashboard

The easiest way to deploy is through the Cloudflare web interface.

### Step 1: Push to Git

First, make sure your project is in a git repository and pushed to a remote:

```bash
cd my-app
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/my-app.git
git push -u origin main
```

### Step 2: Create a Cloudflare Pages Project

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) > Pages
2. Click "Create a project" > "Connect to Git"
3. Authorize Cloudflare to access your GitHub/GitLab account
4. Select your repository

### Step 3: Configure Build Settings

Configure the following build settings:

- **Project name**: `my-app` (or your preferred name)
- **Production branch**: `main`
- **Root directory**: `frontend`
- **Build command**: `pnpm build`
- **Build output directory**: `dist`

Click "Save and Deploy".

That's it. In about 30 seconds, your frontend is live at `https://my-app.pages.dev`.

### Step 4: Configure Environment Variables

Your frontend needs to know where your backend lives and have credentials to authenticate. After deploying your backend to Modal (see [Deploy Backend to Modal](?doc=deploy-modal)), add these environment variables:

1. Go to your project in Cloudflare Pages
2. Click "Settings" > "Environment variables"
3. Click "Add variable" and add the following for **Production**:
   - `VITE_API_URL` = `https://yourusername--my-app-backend-fastapi-app.modal.run`
   - `VITE_MODAL_KEY` = your proxy auth token ID (`wk-xxx`)
   - `VITE_MODAL_SECRET` = your proxy auth token secret (`ws-xxx`)
4. Click "Save"
5. Trigger a new deployment for changes to take effect

**Note:** Get your proxy auth tokens from [modal.com/settings/proxy-auth-tokens](https://modal.com/settings/proxy-auth-tokens).

## Option 2: Deploy via Wrangler CLI

Prefer the command line? Use the Wrangler CLI.

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Log in to Cloudflare

```bash
wrangler login
```

This opens your browser to authenticate with Cloudflare.

### Step 3: Build and Deploy

From your project root:

```bash
cd frontend
pnpm build
wrangler pages deploy dist --project-name=my-app
```

The CLI will create the project if it doesn't exist and deploy your app.

### Step 4: Set Environment Variables

```bash
# Set production environment variables
wrangler pages secret put VITE_API_URL --project-name=my-app
# Enter your Modal production URL when prompted

wrangler pages secret put VITE_MODAL_KEY --project-name=my-app
# Enter your proxy auth token ID when prompted

wrangler pages secret put VITE_MODAL_SECRET --project-name=my-app
# Enter your proxy auth token secret when prompted
```

### Step 5: Redeploy with Environment Variables

```bash
cd frontend
pnpm build
wrangler pages deploy dist --project-name=my-app
```

## How Environment Variables Work

Your FastReact project already includes `frontend/src/lib/api.ts` which handles both the API URL and Modal authentication:

```typescript
const API_URL = import.meta.env.VITE_API_URL || "";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options?.headers,
  };

  // Add Modal auth headers if configured
  const modalKey = import.meta.env.VITE_MODAL_KEY;
  const modalSecret = import.meta.env.VITE_MODAL_SECRET;
  if (modalKey && modalSecret) {
    headers["Modal-Key"] = modalKey;
    headers["Modal-Secret"] = modalSecret;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

Use this utility in your components:

```typescript
import { api } from "@/lib/api";

// Instead of: fetch("/api/hello")
const data = await api<{ message: string }>("/api/hello");
```

**How this works:**

- The `api()` helper automatically includes Modal proxy auth headers
- `VITE_API_URL` points to your Modal backend URL
- `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` authenticate requests

## Set Up Automatic Deployments

Once connected to git, Cloudflare Pages automatically deploys:

- **Production deploys** when you push to `main`
- **Preview deploys** for every pull request

Each preview gets a unique URL like `abc123.my-app.pages.dev`.

## Custom Domain

Want to use your own domain?

1. Go to your project in Cloudflare Pages
2. Click "Custom domains"
3. Click "Set up a custom domain"
4. Add your domain (e.g., `myapp.com`)
5. Update your DNS records as instructed

Cloudflare provisions SSL automatically.

## Verify Your Deployment

After deploying, verify everything works:

1. **Check the build logs** - Make sure there are no errors
2. **Visit your live URL** - The app should load
3. **Test API calls** - After setting up Modal, verify data flows correctly

If API calls fail, check:
- The `VITE_API_URL` environment variable is set correctly
- The `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` are set correctly
- Your Modal backend is deployed and running
- CORS is configured to allow your Cloudflare domain

## Next Steps

Your frontend is live! Now deploy your backend:

- [Deploy Backend to Modal](?doc=deploy-modal) - Get your FastAPI running serverless
- [Add AI Features](?doc=add-ai) - Integrate GPT, embeddings, and more

---

**Tip:** Cloudflare Pages includes Web Analytics for free. Enable it in your project settings to monitor traffic and performance.
