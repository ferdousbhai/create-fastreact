# Why FastReact?

**Python backend, React frontend, AI-powered development.**

FastReact is the fullstack framework for Python developers who want modern web UIs without abandoning their favorite language.

---

## Key Features

- **Python Backend** - FastAPI + Modal serverless. Access the entire Python ecosystem.
- **React Frontend** - Vite + TypeScript + Tailwind. Best-in-class UI development.
- **AI-First** - Built-in autonomous coding agent. Describe your app, let Claude build it.
- **Zero Infrastructure** - Vercel (frontend) + Modal (backend). No servers to manage.

---

## The Problem

The JavaScript ecosystem won the frontend. React, Vue, Svelte—they all deliver excellent UIs.

But modern fullstack frameworks assume JavaScript everywhere. Next.js, Remix, Nuxt—all require TypeScript on both ends. For Python developers, this creates problems:

### Library Lock-out

The Python ecosystem has libraries that don't exist in JavaScript:

- **pandas** for data manipulation
- **scikit-learn** for machine learning
- **OpenCV** for image processing
- **NumPy** for numerical computing

A JavaScript backend means losing access to decades of Python's scientific computing heritage.

### AI Integration Nightmares

Every application wants AI now. Where do the best AI libraries live? **Python.**

- OpenAI, Anthropic SDKs—Python-first
- Hugging Face Transformers—Python
- LangChain—Python-first
- PyTorch, JAX—Python

Building AI-powered apps with Next.js means spinning up a separate Python service anyway. Why not make Python your primary backend?

### Microservices Complexity

The industry learned that microservices create operational nightmares: Kubernetes, service meshes, container orchestration, auto-scaling configs...

What if deploying a Python service was as simple as one command?

---

## The Solution

FastReact combines the best tools for each job:

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | React + Vite + TypeScript | Mature ecosystem, great DX |
| Backend | FastAPI + Python | Full Python library access |
| AI Agent | Claude Code / API | Autonomous feature development |
| Deploy (Frontend) | Vercel | Edge network, zero config |
| Deploy (Backend) | Modal | Serverless Python, GPU support |

### The Architecture

```
┌─────────────────────────────────────────┐
│              Your Application           │
├────────────────────┬────────────────────┤
│     Frontend       │      Backend       │
│  React 19 + Vite   │  FastAPI + Modal   │
│    TypeScript      │      Python        │
│   Tailwind CSS     │   Any Python Lib   │
│     shadcn/ui      │   AI/ML Ready      │
├────────────────────┼────────────────────┤
│      Vercel        │       Modal        │
│   (Edge Network)   │   (Serverless)     │
├────────────────────┴────────────────────┤
│            AI Coding Agent              │
│    Claude Code / Anthropic API          │
│  Autonomous feature implementation      │
└─────────────────────────────────────────┘
```

---

## AI-Powered Development

FastReact includes an autonomous coding agent that builds your app from a description:

```bash
pnpm create fastreact my-app
cd my-app/agent
uv run agent
```

The agent:

1. **Reads your description** in `app_spec.md`
2. **Generates features** breaking down your app into tasks
3. **Implements each feature** with tests
4. **Commits after each feature** for easy review
5. **Continues until complete**

This isn't code generation. It's an autonomous developer that understands your codebase, makes incremental progress, and leaves clean commits you can review.

---

## Why This Architecture Works

### Clean Separation

Frontend handles UI, client state, user interactions. Backend handles data processing, business logic, external integrations.

No "is this a server component or client component?" confusion. React components are always client components. Data flows through API calls.

### AI-Native by Default

GPT-4 integration? Import OpenAI's SDK. Image generation? Import Stability AI. Vector search? Use any embedding library.

Modal's GPU support means you can run inference without managing CUDA drivers.

### Microservices Without Pain

Each Modal function is essentially a microservice. Unlike traditional microservices, there's no operational overhead—Modal handles all infrastructure.

### Type Safety Where It Matters

TypeScript on frontend catches UI bugs at compile time. Python type hints with FastAPI give runtime validation and automatic OpenAPI docs.

---

## Get Started

```bash
pnpm create fastreact my-app
cd my-app/agent
uv run agent
```

You'll have:
- An AI agent building your app
- React 19 frontend with TypeScript and Tailwind
- FastAPI backend on Modal
- Git commits for each feature

**→ [Continue to Quickstart](?doc=get-started)**
