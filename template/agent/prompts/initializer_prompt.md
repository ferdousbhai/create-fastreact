# Initializer Session

You are starting a NEW FastReact project. Your task is to analyze the app description, verify services, and create a comprehensive feature list.

## Step 1: Read the App Specification

Read `app_spec.md` to understand what the user wants to build.

## Step 2: Verify Modal Authentication (CRITICAL)

Before proceeding, verify Modal CLI is authenticated:

```bash
# Check Modal authentication
modal token show
```

**If NOT authenticated:**
1. Run `modal token new` to authenticate
2. If that fails, document in `claude-progress.txt` and warn the user
3. Do NOT proceed with backend features until Modal is authenticated

## Step 3: Set Up Puppeteer MCP for Browser Testing

Update `.mcp.json` to enable browser automation:

```json
{
  "mcpServers": {
    "puppeteer-mcp-claude": {
      "command": "npx",
      "args": ["-y", "puppeteer-mcp-claude", "serve"]
    }
  }
}
```

This enables UI verification through actual browser interactions.

## Step 4: Create init.sh

Create `init.sh` to set up the development environment:

```bash
#!/bin/bash
set -e

echo "Setting up FastReact development environment..."

# Install frontend dependencies
cd frontend
pnpm install
cd ..

# Start development servers
echo ""
echo "Starting development servers..."
echo "  Frontend: http://localhost:5173"
echo "  Backend:  modal serve backend/modal_app.py"
echo ""

# Start frontend in background
cd frontend && pnpm run dev &
FRONTEND_PID=$!

# Start backend
cd ../backend && modal serve modal_app.py &
BACKEND_PID=$!

echo "Servers started. Press Ctrl+C to stop."
wait
```

Make it executable: `chmod +x init.sh`

## Step 5: Create feature_list.json

Based on the app description, create `feature_list.json` as a flat array:

```json
[
  {
    "category": "backend-api",
    "description": "What this feature does and why",
    "steps": ["Step 1 to verify", "Step 2 to verify", "Step 3 to verify"],
    "passes": false
  }
]
```

### Standard Categories for FastReact

Use these categories to organize features:
- `backend-api` - FastAPI endpoints on Modal
- `frontend-ui` - React components and pages
- `state` - State management and data flow
- `auth` - Authentication and authorization
- `styling` - Tailwind/shadcn styling and responsive design
- `integration` - Frontend-backend integration

### Guidelines for Feature Breakdown

1. **Order by dependency**: Backend API first, then frontend integration
2. **One feature per session**: Each should be completable in ~20-30 min
3. **Specific verification steps**: Include exact UI actions to test
4. **15-30 features total**: Adjust based on app complexity
5. **All start with `"passes": false`**

### Required First Features

Always include these foundational features first:
1. Health check endpoint at `/api/health`
2. Root App component renders without errors
3. Frontend can connect to backend API

## Step 6: Set Up Project Structure

Ensure the basic structure exists:
- `frontend/src/` - React source files
- `backend/` - FastAPI on Modal
- `agent/prompts/` - Agent prompts

## Step 7: Initial Commit

```bash
git add -A
git commit -m "Initialize project with feature_list.json and dev setup"
```

## Step 8: Update Progress Notes

Write to `claude-progress.txt`:
- Modal authentication status
- Summary of planned features
- Recommended implementation order
- Any assumptions made

---

**IMPORTANT**: Do NOT implement any features yet. Just create the plan and setup files.
