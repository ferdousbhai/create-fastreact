# Get Started with FastReact

Python backend, React frontend. Describe your app, let AI build it.

By the end of this quickstart, you'll have:
- An AI agent that builds your app from a plain English description
- A React frontend with TypeScript, Tailwind, and shadcn/ui
- A FastAPI backend on Modal (serverless Python)
- Everything ready for production deployment

## Prerequisites

Before you begin, make sure you have:

- **Node.js 18+** and **pnpm** installed
- **Python 3.12+** and **uv** installed
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated

**Note:** The CLI will guide you through Modal installation and authentication during project setup.

Don't have these yet? Here's how to get them:

```bash
# Install pnpm (if you have npm)
npm install -g pnpm

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Create Your Project

Run the create command and follow the prompts:

```bash
pnpm create fastreact my-app
```

The CLI verifies prerequisites (Claude Code, Modal), then prompts for:
- **Project name** - Your app's name
- **App description** - Describe what you want to build in plain English
- **Proxy auth tokens** - Optional, for production security

The CLI will:
1. Create the project structure
2. Set up the frontend (React 19 + Vite + TypeScript + Tailwind)
3. Set up the backend (FastAPI + Python 3.12)
4. Set up the AI agent
5. Generate `app_spec.md` from your description
6. Install all dependencies
7. Initialize a git repository

Once complete, navigate to the agent directory:

```bash
cd my-app/agent
```

## Run the AI Agent

This is where the magic happens. The AI agent reads your app description and builds it for you:

```bash
uv run agent
```

The agent uses your Claude Code authentication.

### What the Agent Does

**Session 1 (Initializer):**
- Reads your `app_spec.md`
- Breaks down your description into discrete features
- Creates `feature_list.json` with all features to implement
- Commits: "Initialize project with feature_list.json"

**Session 2+ (Coding):**
- Picks the next incomplete feature
- Implements it in frontend/ and/or backend/
- Tests the feature
- Marks it complete in `feature_list.json`
- Commits: "feat: <description>"
- Repeats until all features are done

### Monitor Progress

- `feature_list.json` - Track which features are done
- `claude-progress.txt` - Session notes from the AI
- `git log` - See commits for each feature

Press `Ctrl+C` to pause. Resume anytime with `uv run agent --continue` from the agent directory.

## Manual Development

If you prefer to code manually (or want to work alongside the agent):

```bash
pnpm run dev
```

This starts both frontend and backend:

```
[frontend] VITE v6.x.x  ready in 300ms
[frontend] ➜  Local:   http://localhost:5173/
[backend]  ✓ Created objects.
[backend]  └── 🔨 Created fastapi_app => https://yourusername--my-app-backend-fastapi-app-dev.modal.run
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

**Note:** The backend runs on Modal's cloud, not locally. This gives you the same environment in development and production.

## Explore the Project Structure

Let's look at what was created:

```
my-app/
├── package.json          # Root config with dev scripts
├── app_spec.md           # Your app description (AI reads this)
├── feature_list.json     # AI-generated feature list
├── claude-progress.txt   # AI session notes
├── frontend/
│   ├── src/
│   │   ├── App.tsx       # Your React application
│   │   ├── main.tsx      # Entry point
│   │   ├── index.css     # Tailwind styles
│   │   └── lib/
│   │       └── api.ts    # API helper with Modal auth
│   ├── vite.config.ts    # Vite config
│   └── package.json
├── backend/
│   ├── app/
│   │   └── main.py       # Your FastAPI application
│   ├── modal_app.py      # Modal deployment config
│   └── pyproject.toml    # Python dependencies
└── agent/
    ├── agent.py          # AI coding agent
    ├── .env.example      # Environment config template
    └── prompts/          # Customizable AI prompts
        ├── initializer_prompt.md
        └── coding_prompt.md
```

**Key files:**
- `app_spec.md` - Your app description. Edit this to change what the AI builds.
- `feature_list.json` - The AI's task list. Features are marked `passes: true` when complete.
- `agent/` - The autonomous coding agent that builds your app.

## Your First API Call

Let's connect the frontend to the backend. The backend already has a sample endpoint. Let's call it from React.

### Step 1: Check the Backend Endpoint

Open `backend/app/main.py`. You'll see:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/hello")
def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}
```

The `/api/hello` endpoint accepts an optional `name` parameter and returns a greeting.

### Step 2: Understand the API Helper

Open `frontend/src/lib/api.ts`. This helper handles Modal's proxy authentication:

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

**Always use this `api()` helper** instead of raw `fetch()`. It automatically includes the Modal authentication headers needed to call your backend.

### Step 3: Call the API from React

Replace the contents of `frontend/src/App.tsx` with:

```tsx
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function App() {
  const [message, setMessage] = useState<string>("");
  const [name, setName] = useState<string>("");

  async function fetchGreeting(name: string) {
    const params = name ? `?name=${encodeURIComponent(name)}` : "";
    const data = await api<{ message: string }>(`/api/hello${params}`);
    setMessage(data.message);
  }

  useEffect(() => {
    fetchGreeting("");
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold">{message || "Loading..."}</h1>

      <div className="flex gap-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          className="rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={() => fetchGreeting(name)}
          className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Greet Me
        </button>
      </div>
    </div>
  );
}
```

Save the file. Thanks to hot reloading, your browser updates automatically.

### Step 4: Test It

1. The page loads with "Hello, world!"
2. Type your name in the input field
3. Click "Greet Me"
4. The message updates to greet you personally

**What just happened?** Your React component called your FastAPI backend running on Modal. The `api()` helper included your Modal proxy auth credentials, authenticating the request.

## Add a New Endpoint

Let's create a more interesting endpoint. We'll build a simple counter that persists in memory.

### Step 1: Add the Backend Logic

Open `backend/app/main.py` and add:

```python
# Add this after the existing endpoints

counter = {"value": 0}

@app.get("/api/counter")
def get_counter():
    return counter

@app.post("/api/counter/increment")
def increment_counter():
    counter["value"] += 1
    return counter

@app.post("/api/counter/decrement")
def decrement_counter():
    counter["value"] -= 1
    return counter
```

The backend automatically reloads when you save.

### Step 2: Create the Counter Component

Create a new file `frontend/src/Counter.tsx`:

```tsx
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function Counter() {
  const [count, setCount] = useState<number | null>(null);

  async function fetchCount() {
    const data = await api<{ value: number }>("/api/counter");
    setCount(data.value);
  }

  async function increment() {
    const data = await api<{ value: number }>("/api/counter/increment", {
      method: "POST",
    });
    setCount(data.value);
  }

  async function decrement() {
    const data = await api<{ value: number }>("/api/counter/decrement", {
      method: "POST",
    });
    setCount(data.value);
  }

  useEffect(() => {
    fetchCount();
  }, []);

  return (
    <div className="flex flex-col items-center gap-4 rounded-lg border p-6">
      <h2 className="text-2xl font-semibold">Server Counter</h2>
      <p className="text-5xl font-bold">{count ?? "..."}</p>
      <div className="flex gap-2">
        <button
          onClick={decrement}
          className="rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
        >
          -1
        </button>
        <button
          onClick={increment}
          className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
        >
          +1
        </button>
      </div>
      <p className="text-sm text-gray-500">
        This counter lives on the server. Open another tab to see it sync!
      </p>
    </div>
  );
}
```

### Step 3: Add the Counter to App

Update `frontend/src/App.tsx` to include the counter:

```tsx
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import Counter from "./Counter";

export default function App() {
  const [message, setMessage] = useState<string>("");
  const [name, setName] = useState<string>("");

  async function fetchGreeting(name: string) {
    const params = name ? `?name=${encodeURIComponent(name)}` : "";
    const data = await api<{ message: string }>(`/api/hello${params}`);
    setMessage(data.message);
  }

  useEffect(() => {
    fetchGreeting("");
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <h1 className="text-4xl font-bold">{message || "Loading..."}</h1>

      <div className="flex gap-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          className="rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={() => fetchGreeting(name)}
          className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Greet Me
        </button>
      </div>

      <Counter />
    </div>
  );
}
```

### Step 4: See Server State in Action

1. Click the +1 and -1 buttons to change the counter
2. Open the same URL in a new browser tab
3. Click a button in either tab
4. Refresh the other tab—the count is shared!

**This demonstrates a key concept:** The counter state lives on your FastAPI server, not in the browser. Both tabs are talking to the same backend.

## What You Built

Let's recap what you accomplished:

- **Described your app** in plain English
- **AI generated a feature list** breaking down your app into tasks
- **AI implements features** one by one with testing and commits
- **Created a fullstack project** with React and FastAPI
- **Connected frontend to backend** via API calls

## Configuring the Agent

### Customizing Prompts

Edit the prompts in `agent/prompts/` to change how the AI works:
- `initializer_prompt.md` - How features are broken down
- `coding_prompt.md` - How features are implemented

## Next Steps

Now that you have a working app, here's where to go next:

### Deploy to Production

- [Deploy Frontend to Cloudflare](?doc=deploy-cloudflare) - Get your React app on the edge
- [Deploy Backend to Modal](?doc=deploy-modal) - Serverless Python with one command

### Add More Features

- [Add AI Features](?doc=add-ai) - Integrate OpenAI, Hugging Face, and more

### Learn the Stack

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Deep dive into Python APIs
- [React Documentation](https://react.dev/) - Master component patterns
- [Modal Documentation](https://modal.com/docs) - Serverless deployment guide
- [Anthropic Autonomous Coding](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) - The architecture behind our agent

---

**You're ready to build.** Describe what you want, let AI build it. FastReact gives you the best of both worlds: a modern React frontend and a powerful Python backend, built by AI.
