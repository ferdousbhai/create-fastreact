#!/bin/bash
# create-fastreact Development Environment Setup
# ================================================
# This script sets up the development environment for the create-fastreact CLI tool.

set -e

echo "🚀 Setting up create-fastreact development environment..."
echo ""

# Check for required tools
command -v pnpm >/dev/null 2>&1 || { echo "❌ pnpm is required but not installed. Install: https://pnpm.io/"; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "❌ uv is required but not installed. Install: https://docs.astral.sh/uv/"; exit 1; }

# Install CLI dependencies
echo "📦 Installing CLI dependencies..."
pnpm install

# Build the CLI
echo "🔨 Building CLI..."
pnpm run build

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Test the CLI locally:"
echo "      node dist/index.js"
echo ""
echo "   2. Or link globally for testing:"
echo "      pnpm link --global"
echo "      create-fastreact my-test-app"
echo ""
echo "   3. For development with watch mode:"
echo "      pnpm run dev"
echo ""
