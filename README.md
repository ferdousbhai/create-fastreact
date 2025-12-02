# create-fastreact

AI-first full-stack framework. Describe your app, let AI build it.

```bash
pnpm create fastreact my-app
```

## What you get

- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4 + shadcn/ui
- **Backend**: FastAPI on Modal (serverless Python)
- **AI Agent**: Autonomous coding agent that builds your app from a description
- **Deployment**: Vercel (frontend) + Modal (backend)

## How it works

1. **Describe your app** in plain English
2. **AI creates a feature list** from your description
3. **AI implements features** one by one, testing each
4. **You review and iterate** as it builds

Based on [Anthropic's autonomous coding architecture](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [pnpm](https://pnpm.io/)
- [Python](https://www.python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Modal CLI](https://modal.com/docs/guide) (logged in)
- **One of:**
  - [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (recommended - uses existing subscription), OR
  - [Anthropic API key](https://console.anthropic.com/) (pay per use)

## Quick Start

1. Create your app:
```bash
pnpm create fastreact my-app
```

You'll be prompted for:
- Project name
- Modal username (auto-detected)
- App description (plain English)
- Proxy auth tokens (optional)

2. Run the AI agent:
```bash
cd my-app/agent
uv run agent
```

The agent auto-detects your auth method (in order):
1. **Claude Code** installed → uses existing subscription (no extra cost)
2. **ANTHROPIC_API_KEY** set → uses API directly

Or specify explicitly:
```bash
uv run agent --claude-code    # Use Claude Code
uv run agent --api            # Use API key
```

The agent will:
- **Session 1 (Initializer)**: Create `feature_list.json` from your description
- **Session 2+ (Coding)**: Implement features one by one

3. Monitor progress:
- `feature_list.json` - Track which features are done
- `claude-progress.txt` - Session notes from the AI
- `git log` - See commits for each feature

## Manual Development

If you want to code manually instead of using the agent:

```bash
cd my-app
pnpm run dev
```

- Frontend: http://localhost:5173
- Backend: Your Modal dev endpoint

## Project Structure

```
my-app/
├── frontend/           # React + Vite + Tailwind
├── backend/            # FastAPI on Modal
├── agent/              # AI coding agent
│   ├── agent.py        # Main agent script
│   ├── prompts/        # Customizable prompts
│   └── .env.example    # Environment config template
├── app_spec.md         # Your app description
├── feature_list.json   # AI-generated feature list
└── claude-progress.txt # AI session notes
```

## Configuring the Agent

### Environment Variables

For `--api` mode only (Claude Code handles its own config):

```bash
ANTHROPIC_API_KEY=sk-ant-...
FASTREACT_INITIALIZER_MODEL=claude-opus-4-5-20251101  # optional
FASTREACT_CODING_MODEL=claude-sonnet-4-5-20250929    # optional, saves costs
```

### Customizing Prompts

Edit the prompts in `agent/prompts/`:
- `initializer_prompt.md` - How features are broken down
- `coding_prompt.md` - How features are implemented

## Why fastreact?

- **AI-first**: Describe what you want, AI builds it
- **Full-stack**: React frontend + FastAPI backend
- **Serverless**: Deploy to Modal with zero infrastructure
- **Modern stack**: Vite, Tailwind v4, shadcn/ui, TypeScript
- **Incremental**: AI commits after each feature, easy to review

## Deployment

### Backend

```bash
cd backend
modal deploy modal_app.py
```

### Frontend

```bash
cd frontend
vercel
```

Set environment variables in Vercel:
- `VITE_API_URL` - Modal production URL
- `VITE_MODAL_KEY` - Proxy auth token ID
- `VITE_MODAL_SECRET` - Proxy auth token secret

## License

MIT
