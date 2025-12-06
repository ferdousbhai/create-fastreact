# Deploy Frontend to Vercel

Get your FastReact frontend live on the edge in under 5 minutes.

Vercel is purpose-built for frontend frameworks like React + Vite. It provides:

- **Global edge network** - Your app loads fast everywhere
- **Automatic HTTPS** - SSL certificates handled for you
- **Preview deployments** - Every git branch gets its own URL
- **Zero configuration** - Vite projects work out of the box

## Prerequisites

- A FastReact project (run `pnpm create fastreact my-app` if you haven't)
- A [Vercel account](https://vercel.com/signup) (free tier works great)
- Your code pushed to GitHub, GitLab, or Bitbucket

## Option 1: Deploy via Vercel Dashboard

The easiest way to deploy is through the Vercel web interface.

### Step 1: Push to Git

First, make sure your project is in a git repository and pushed to a remote:

```bash
cd my-app
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/my-app.git
git push -u origin main
```

### Step 2: Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import" next to your repository
3. **Important:** Set the Root Directory to `frontend`
4. Vercel auto-detects Vite—no build settings needed
5. Click "Deploy"

That's it. In about 30 seconds, your frontend is live.

### Step 3: Configure Environment Variables

Your frontend needs to know where your backend lives and have credentials to authenticate. After deploying your backend to Modal (see [Deploy Backend to Modal](?doc=deploy-modal)), add these environment variables:

1. Go to your project settings in Vercel
2. Click "Environment Variables"
3. Add the following:
   - `VITE_API_URL` = `https://yourusername--my-app-backend-fastapi-app.modal.run`
   - `VITE_MODAL_KEY` = your proxy auth token ID (`wk-xxx`)
   - `VITE_MODAL_SECRET` = your proxy auth token secret (`ws-xxx`)
4. Redeploy for changes to take effect

**Note:** Get your proxy auth tokens from [modal.com/settings/proxy-auth-tokens](https://modal.com/settings/proxy-auth-tokens).

## Option 2: Deploy via CLI

Prefer the command line? Use the Vercel CLI.

### Step 1: Install Vercel CLI

```bash
pnpm add -g vercel
```

### Step 2: Deploy

From your project root:

```bash
cd frontend
vercel
```

The CLI will ask a few questions:

```
? Set up and deploy "my-app/frontend"? Yes
? Which scope do you want to deploy to? Your Account
? Link to existing project? No
? What's your project's name? my-app
? In which directory is your code located? ./
```

Vercel detects Vite automatically and deploys.

### Step 3: Deploy to Production

The first deploy creates a preview URL. To deploy to production:

```bash
vercel --prod
```

## Update Vite Config for Production

Your `frontend/vite.config.ts` needs to handle both development and production API URLs.

Update it to use environment variables:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

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

Once connected to git, Vercel automatically deploys:

- **Production deploys** when you push to `main`
- **Preview deploys** for every pull request

Each preview gets a unique URL like `my-app-git-feature-branch-yourname.vercel.app`.

## Custom Domain

Want to use your own domain?

1. Go to your project settings in Vercel
2. Click "Domains"
3. Add your domain (e.g., `myapp.com`)
4. Update your DNS records as instructed

Vercel provisions SSL automatically.

## Verify Your Deployment

After deploying, verify everything works:

1. **Check the build logs** - Make sure there are no errors
2. **Visit your live URL** - The app should load
3. **Test API calls** - After setting up Modal, verify data flows correctly

If API calls fail, check:
- The `VITE_API_URL` environment variable is set correctly
- The `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` are set correctly
- Your Modal backend is deployed and running
- CORS is configured to allow your Vercel domain

## Next Steps

Your frontend is live! Now deploy your backend:

- [Deploy Backend to Modal](?doc=deploy-modal) - Get your FastAPI running serverless
- [Add AI Features](?doc=add-ai) - Integrate GPT, embeddings, and more

---

**Tip:** Enable Vercel Analytics to monitor your frontend performance. It's free for hobby projects and gives you Core Web Vitals tracking.
