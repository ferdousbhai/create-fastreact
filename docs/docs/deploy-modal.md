# Deploy Backend to Modal

Get your FastAPI backend running serverless with GPU support in minutes.

Modal is a serverless platform built specifically for Python. It handles:

- **Automatic scaling** - From zero to thousands of concurrent requests
- **GPU support** - Run ML models with one decorator
- **Container management** - Define dependencies in Python, not Dockerfiles
- **Pay-per-use** - Only pay when your code runs

## Prerequisites

- A FastReact project with a working backend
- A [Modal account](https://modal.com/signup) (free tier includes $30/month credits)
- Python 3.12 and `uv` installed

## Step 1: Set Up Modal

First, install and authenticate the Modal CLI:

```bash
# Install modal (already in your pyproject.toml)
cd backend
uv sync

# Authenticate with Modal
uv run modal setup
```

This opens a browser to authenticate. Once done, you're connected to Modal.

## Step 2: Understand the Modal Config

Your FastReact project includes a `modal_app.py` file. Let's break it down:

```python
import modal

app = modal.App("my-app-backend")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("uv")
    .add_local_file("pyproject.toml", "/app/pyproject.toml")
    .add_local_dir("app", "/app/app")
    .run_commands("cd /app && uv pip install --system -r pyproject.toml")
)


@app.function(image=image)
@modal.asgi_app(requires_proxy_auth=True)
def fastapi_app():
    from app.main import app

    return app
```

**What's happening here:**

1. **`modal.App`** - Creates a Modal application with a unique name
2. **`modal.Image`** - Defines the container with Python 3.12, uv, and your dependencies
3. **`@modal.asgi_app`** - Exposes your FastAPI app as an ASGI web endpoint
4. **`requires_proxy_auth=True`** - Requires proxy authentication via `Modal-Key` and `Modal-Secret` headers

## Step 3: Test Locally with Modal

Before deploying, test that Modal can run your app:

```bash
cd backend
uv run modal serve modal_app.py
```

This starts your app in Modal's cloud with a temporary URL. You'll see output like:

```
✓ Created objects.
├── 🔨 Created mount /app
└── 🔨 Created fastapi_app => https://yourusername--my-app-backend-fastapi-app-dev.modal.run
```

Open that URL in your browser. You should see your FastAPI app's JSON response.

Press `Ctrl+C` to stop the server.

## Step 4: Deploy to Production

When you're ready to go live:

```bash
cd backend
uv run modal deploy modal_app.py
```

Modal builds your container, deploys it, and gives you a permanent URL:

```
✓ Deployed app: my-app-backend
└── 🔨 Created fastapi_app => https://yourusername--my-app-backend-fastapi-app.modal.run
```

**This URL is your production API.** Save it—you'll need it for your frontend.

## Step 5: Configure Authentication

The `requires_proxy_auth=True` setting means your API requires proxy authentication. This prevents unauthorized access.

### Get Your Proxy Auth Tokens

1. Go to [modal.com/settings/proxy-auth-tokens](https://modal.com/settings/proxy-auth-tokens)
2. Click "Create new token"
3. You'll get:
   - A token ID starting with `wk-`
   - A token secret starting with `ws-`

**Note:** The CLI already asked for these during `pnpm create fastreact`. They're stored in `frontend/.env.local`.

### Call Your Authenticated API

When making requests, include the proxy auth headers:

```bash
curl -H "Modal-Key: wk-your-token-id" \
     -H "Modal-Secret: ws-your-token-secret" \
  https://yourusername--my-app-backend-fastapi-app.modal.run/api/hello
```

### For Frontend Integration

Your FastReact project already includes `frontend/src/lib/api.ts`:

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

In Cloudflare Pages, add these environment variables:
- `VITE_API_URL` = `https://yourusername--my-app-backend-fastapi-app.modal.run`
- `VITE_MODAL_KEY` = `wk-your-token-id`
- `VITE_MODAL_SECRET` = `ws-your-token-secret`

### Alternative: Public Endpoints

If you want public endpoints (no auth), remove `requires_proxy_auth`:

```python
@app.function(image=image)
@modal.asgi_app()  # No auth required
def fastapi_app():
    from app.main import app
    return app
```

**Warning:** Only do this if your API doesn't handle sensitive data.

## Step 6: Add GPU Support

Need to run ML models? Add GPU support with one parameter:

```python
@app.function(image=image, gpu="T4")  # Add GPU
@modal.asgi_app()
def fastapi_app():
    from app.main import app
    return app
```

Available GPU options:
- `"T4"` - Good for inference, cheapest option
- `"A10G"` - More VRAM, faster inference
- `"A100"` - Maximum power for training and large models

## Step 7: Add Python Dependencies

When you add new Python packages, update your `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "modal>=0.68.0",
    "uvicorn>=0.32.0",
    "openai>=1.0.0",        # Add new packages here
    "numpy>=1.26.0",
]
```

Then redeploy:

```bash
uv sync  # Update local environment
uv run modal deploy modal_app.py  # Redeploy
```

Modal rebuilds the container with your new dependencies.

## Monitor Your Deployment

Modal provides built-in monitoring:

1. Go to [modal.com/apps](https://modal.com/apps)
2. Click on your app
3. View logs, metrics, and invocations

You can see:
- Request logs in real-time
- Cold start times
- Memory and CPU usage
- Error traces

## Update Your Deployment

To push changes:

```bash
cd backend
uv run modal deploy modal_app.py
```

Modal performs a rolling update—no downtime.

## Cost Optimization

Modal charges per-second of compute. To minimize costs:

1. **Use appropriate resources** - Don't request a GPU if you don't need one
2. **Optimize cold starts** - Keep your image small
3. **Set concurrency limits** - Prevent runaway scaling

```python
@app.function(
    image=image,
    concurrency_limit=10,  # Max 10 concurrent instances
    container_idle_timeout=60,  # Keep warm for 60s
)
```

## Troubleshooting

### "Module not found" errors

Make sure your dependencies are in `pyproject.toml` and run `uv sync` before deploying.

### Slow cold starts

Reduce image size by only installing what you need. Avoid large ML libraries unless required.

### CORS errors

Update your FastAPI CORS configuration to include your Cloudflare Pages domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.pages.dev",
        "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

Your backend is live! Continue building:

- [Add AI Features](?doc=add-ai) - Integrate OpenAI, Hugging Face, and more

---

**Tip:** Use `modal serve` during development for instant feedback. It's faster than full deploys and shows real-time logs.
