#!/bin/bash
# FastReact Development Environment Setup

set -e

echo "Setting up development environment..."

# Check for required tools
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required but not installed. Install: https://pnpm.io/"; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "uv is required but not installed. Install: https://docs.astral.sh/uv/"; exit 1; }
command -v modal >/dev/null 2>&1 || { echo "modal is required but not installed. Install: uv tool install modal"; exit 1; }

# Install dependencies
echo "Installing frontend dependencies..."
(cd frontend && pnpm install)

echo "Installing backend dependencies..."
(cd backend && uv sync)

echo "Installing agent dependencies..."
(cd agent && uv sync)

echo ""
echo "Setup complete!"
echo ""
echo "To start development:"
echo "  Frontend: cd frontend && pnpm run dev"
echo "  Backend:  cd backend && modal serve modal_app.py"
echo ""
echo "To run the AI agent:"
echo "  cd agent && uv run agent"
