# create-fastreact

The best way to start a full-stack React + FastAPI app.

```bash
pnpm create fastreact my-app
```

## What you get

- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4 + shadcn/ui
- **Backend**: FastAPI on Modal (serverless)
- **Deployment**: Vercel (frontend) + Modal (backend)

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [pnpm](https://pnpm.io/)
- [Python](https://www.python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Modal CLI](https://modal.com/docs/guide) (logged in)

## Quick Start

1. Create your app:
```bash
pnpm create fastreact my-app
```

You'll be prompted for:
- Project name
- Modal username (auto-detected if logged in)
- Proxy auth tokens (optional for development)

2. Start developing:
```bash
cd my-app
pnpm run dev
```

- Frontend: http://localhost:5173
- Backend: Your Modal endpoint (configured automatically)

## Why fastreact?

If you prefer Python for backend but love the React ecosystem, fastreact gives you the best of both worlds:

- **Type-safe frontend** with TypeScript and shadcn/ui
- **Fast backend** with FastAPI and automatic OpenAPI docs
- **Serverless deployment** with Modal (no infrastructure to manage)
- **Modern tooling** with Vite, Tailwind v4, and uv
- **Zero config** - Modal credentials configured automatically

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

Set these environment variables in Vercel:
- `VITE_API_URL` - Your Modal production URL (without `-dev`)
- `VITE_MODAL_KEY` - Your proxy auth token ID
- `VITE_MODAL_SECRET` - Your proxy auth token secret

## License

MIT
