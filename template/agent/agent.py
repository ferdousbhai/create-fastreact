#!/usr/bin/env python3
"""
FastReact Autonomous Coding Agent
=================================

Two-phase autonomous coding agent:
1. Initializer: Reads app_spec.md and generates feature_list.json
2. Coder: Implements features from feature_list.json incrementally

Runs via Claude Code CLI using your existing Claude Code authentication.

Based on Anthropic's autonomous-coding architecture:
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Literal

DELAY_BETWEEN_SESSIONS = 3


def has_claude_code() -> bool:
    """Check if Claude Code CLI is available."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# =============================================================================
# Progress Tracking
# =============================================================================

def load_feature_list(project_dir: Path) -> list | dict | None:
    """Load feature_list.json from project directory."""
    feature_file = project_dir / "feature_list.json"
    if not feature_file.exists():
        return None
    try:
        with open(feature_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def count_passing_features(project_dir: Path) -> tuple[int, int]:
    """Count passing features from feature_list.json.

    Supports two formats:
    1. Flat array: [{"passes": true}, ...]
    2. Nested categories: {"categories": [{"features": [{"passes": true}]}]}
    """
    data = load_feature_list(project_dir)
    if not data:
        return 0, 0

    total = 0
    passing = 0

    if isinstance(data, list):
        for feature in data:
            total += 1
            if feature.get("passes", False):
                passing += 1
    elif isinstance(data, dict):
        for category in data.get("categories", []):
            for feature in category.get("features", []):
                total += 1
                if feature.get("passes", False):
                    passing += 1

    return passing, total


def print_progress(project_dir: Path):
    """Print progress bar."""
    passing, total = count_passing_features(project_dir)

    if total == 0:
        print("📋 No feature_list.json found - run the CLI first")
        return

    pct = (passing / total) * 100 if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * passing / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"📊 Progress: [{bar}] {passing}/{total} ({pct:.1f}%)")


# =============================================================================
# Agent Session
# =============================================================================

SYSTEM_PROMPT = """You are an expert full-stack developer building a FastReact application.

## Project Structure
- frontend/ - React 19 + TypeScript + Vite + Tailwind v4 + shadcn/ui
- backend/ - FastAPI on Modal (serverless Python)
- agent/ - This autonomous agent

## Development Commands
- Frontend: cd frontend && pnpm run dev (http://localhost:5173)
- Backend: cd backend && modal serve modal_app.py
- Add UI components: cd frontend && pnpm dlx shadcn@latest add <component>

## Rules
- Write clean, maintainable code
- Commit after completing work: git add -A && git commit -m "..."
- Update claude-progress.txt with session notes
"""

INITIALIZER_PROMPT = """# Initializer Session

You are starting a NEW project. Your task is to analyze the app description and create a comprehensive feature list.

## Step 1: Read the App Specification
Read `app_spec.md` to understand what the user wants to build.

## Step 2: Create feature_list.json
Based on the app description, create `feature_list.json` as a flat array:

```json
[
  {
    "category": "Category Name",
    "description": "What this feature does and why",
    "steps": ["Step 1 to verify", "Step 2 to verify", "Step 3 to verify"],
    "passes": false
  }
]
```

## Guidelines for Feature Breakdown
1. Group features by category (e.g., "api", "auth", "core", "ui")
2. Each feature should be small enough to implement in one session (~30 min of work)
3. Include specific, verifiable test steps for each feature
4. Order features by dependency (foundational features first)
5. Start with API/backend setup, then frontend
6. Include 15-30 features total depending on app complexity
7. All features start with "passes": false

## Step 3: Set Up Project Structure
Create any necessary directories or placeholder files for the planned architecture.

## Step 4: Initial Commit
```bash
git add -A
git commit -m "Initialize project with feature_list.json"
```

## Step 5: Update Progress
Write to `claude-progress.txt`:
- Summary of planned features
- Recommended implementation order
- Any assumptions made

IMPORTANT: Do NOT implement any features yet. Just create the plan in feature_list.json.
"""

CODING_PROMPT = """# Coding Session

Continue implementing the application from feature_list.json.

## Step 1: Orient Yourself (MANDATORY)

Start by reading these files to understand the project state:
1. `feature_list.json` - see all features and progress
2. `claude-progress.txt` - notes from previous sessions
3. `git log --oneline -5` - recent commits
4. `app_spec.md` - full app requirements

## Step 2: Verify Before Building

If there are passing features, verify 1-2 core ones still work:
- Run `pnpm run dev` from project root
- Test a key user flow through the UI
- If anything is broken, fix it BEFORE new work

## Step 3: Select Next Feature

Find the first feature where `"passes": false`. This is your focus.

## Step 4: Implement the Feature

Write code in:
- `frontend/` - React 19 + TypeScript + Tailwind v4 + shadcn/ui
- `backend/` - FastAPI on Modal

Add UI components: `cd frontend && pnpm dlx shadcn@latest add <name>`

## Step 5: Test Thoroughly

1. Run `pnpm run dev` from project root (if not running)
2. Verify the feature works per its `steps` array at http://localhost:5173
3. Check browser console for errors

## Step 6: Mark Complete

Update `feature_list.json` - set `"passes": true`
ONLY change the `passes` field - NEVER edit descriptions or steps.

## Step 7: Commit

```bash
git add -A
git commit -m "feat: <description>"
```

## Step 8: Update Progress Notes

Append to `claude-progress.txt`:
- What you completed
- Any issues encountered
- Notes for next session

This context helps the next session pick up where you left off.

## Rules

1. ONE feature per session - complete and commit before moving on
2. Test before marking complete - verify through the actual UI
3. Leave codebase working - no broken features when you exit
4. Document your work - claude-progress.txt is the handoff
"""


def load_prompt(project_dir: Path, is_initializer: bool) -> str:
    """Load the appropriate prompt based on session type."""
    if is_initializer:
        prompt_file = project_dir / "agent" / "prompts" / "initializer_prompt.md"
        default = INITIALIZER_PROMPT
    else:
        prompt_file = project_dir / "agent" / "prompts" / "coding_prompt.md"
        default = CODING_PROMPT

    if prompt_file.exists():
        return prompt_file.read_text()
    return default


def run_session(
    project_dir: Path,
    is_initializer: bool = False,
) -> tuple[Literal["continue", "complete", "error"], str]:
    """Run a session using Claude Code CLI."""
    user_prompt = load_prompt(project_dir, is_initializer)

    # Combine system prompt and user prompt for Claude Code
    full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\n{user_prompt}"

    print("\n🤖 Running via Claude Code...")

    try:
        # Run Claude Code with the prompt
        # --print outputs without interactive mode
        # --dangerously-skip-permissions allows tool use without prompts
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--dangerously-skip-permissions",
                "-p", full_prompt,
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout per session
        )

        if result.returncode != 0:
            return "error", f"Claude Code error: {result.stderr}"

        output = result.stdout
        print(f"\n{output[:2000]}{'...' if len(output) > 2000 else ''}")

        return "continue", output

    except subprocess.TimeoutExpired:
        return "error", "Session timed out (10 minutes)"
    except Exception as e:
        return "error", f"Claude Code error: {e}"


def run_agent(
    project_dir: Path,
    max_iterations: int | None = None,
):
    """Run the autonomous coding agent."""
    project_dir = project_dir.resolve()

    print(f"\n📁 Project: {project_dir}")
    print("🤖 Mode: Claude Code CLI")

    # Check for app_spec.md
    if not (project_dir / "app_spec.md").exists():
        print("\n❌ app_spec.md not found!")
        print("   Run 'pnpm create fastreact' first to initialize the project.")
        sys.exit(1)

    # Determine if we need to run initializer (no feature_list.json yet)
    needs_init = not (project_dir / "feature_list.json").exists()

    session = 1
    iteration = 0

    while True:
        if max_iterations and iteration >= max_iterations:
            print(f"\n⏹️  Max iterations reached ({max_iterations})")
            break

        is_initializer = needs_init and iteration == 0

        print(f"\n{'='*60}")
        if is_initializer:
            print(f"SESSION {session}: INITIALIZER")
        else:
            print(f"SESSION {session}: CODING")
        print("=" * 60)
        print_progress(project_dir)

        # Run session
        status, response = run_session(project_dir, is_initializer)

        print(f"\n📝 Session {session}: {status}")

        # After initializer, check that feature_list.json was created
        if is_initializer:
            if (project_dir / "feature_list.json").exists():
                print("\n✅ feature_list.json created!")
            else:
                print("\n⚠️  feature_list.json not created - will retry")

        passing, total = count_passing_features(project_dir)
        if total > 0 and passing == total:
            print("\n🎉 All features complete!")
            break

        if status == "error":
            print(f"\n❌ {response}")

        session += 1
        iteration += 1

        if max_iterations is None or iteration < max_iterations:
            print(f"\n⏳ Next session in {DELAY_BETWEEN_SESSIONS}s (Ctrl+C to pause)...")
            time.sleep(DELAY_BETWEEN_SESSIONS)


def main():
    parser = argparse.ArgumentParser(
        description="FastReact Autonomous Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Runs via Claude Code CLI using your existing authentication.

Requirements:
  Claude Code CLI must be installed. Get it at:
  https://docs.anthropic.com/en/docs/claude-code

Examples:
  uv run agent                    # Run the agent
  uv run agent --max-iterations 5 # Run at most 5 sessions
        """,
    )
    parser.add_argument("--max-iterations", type=int, help="Max iterations")
    args = parser.parse_args()

    # Check that Claude Code CLI is available
    if not has_claude_code():
        print("❌ Claude Code CLI not found")
        print("\nInstall Claude Code: https://docs.anthropic.com/en/docs/claude-code")
        sys.exit(1)

    # Project is parent of agent/
    project_dir = Path(__file__).parent.parent

    try:
        run_agent(
            project_dir,
            max_iterations=args.max_iterations,
        )
    except KeyboardInterrupt:
        print("\n\n⏸️  Paused. Resume with: uv run agent")


if __name__ == "__main__":
    main()
