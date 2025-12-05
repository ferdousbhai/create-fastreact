#!/usr/bin/env python3
"""
FastReact Autonomous Coding Agent
=================================

Two-phase autonomous coding agent:
1. Initializer: Reads app_spec.md and generates feature_list.json
2. Coder: Implements features from feature_list.json incrementally

Supports two modes:
- API Key: Set ANTHROPIC_API_KEY to use direct API access
- Claude Code: Uses your existing Claude Code authentication

Based on Anthropic's autonomous-coding architecture:
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
"""

import argparse
import asyncio
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env file from agent directory
load_dotenv(Path(__file__).parent / ".env")

DEFAULT_MODEL = "claude-opus-4-5-20251101"
DELAY_BETWEEN_SESSIONS = 3

# Environment variables:
# ANTHROPIC_API_KEY           - API key for direct API access
# FASTREACT_INITIALIZER_MODEL - Model for initializer session (API mode only, default: claude-opus-4-5-20251101)
# FASTREACT_CODING_MODEL      - Model for coding sessions (API mode only, default: claude-opus-4-5-20251101)
#                               Set to claude-sonnet-4-5-20250929 to save costs
# Note: When using Claude Code mode, model selection is handled by Claude Code itself.


def get_model(is_initializer: bool) -> str:
    """Get the model to use based on session type and env vars."""
    if is_initializer:
        return os.environ.get("FASTREACT_INITIALIZER_MODEL", DEFAULT_MODEL)
    else:
        return os.environ.get("FASTREACT_CODING_MODEL", DEFAULT_MODEL)


def has_api_key() -> bool:
    """Check if ANTHROPIC_API_KEY is set."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


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
# Security: Bash Command Validation
# =============================================================================

ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "grep", "find", "wc", "diff", "file",
    "cp", "mv", "mkdir", "rm", "touch", "chmod",
    "git",
    "npm", "npx", "pnpm", "node", "tsc",
    "python", "python3", "pip", "uv", "modal", "uvicorn",
    "curl", "wget", "echo", "printf", "which", "pwd", "cd", "export",
    "pkill", "kill", "ps",
}


def extract_commands(bash_command: str) -> list[str]:
    """Extract command names from a bash command string."""
    segments = []
    current = ""
    i = 0

    while i < len(bash_command):
        char = bash_command[i]
        if char == ";":
            if current.strip():
                segments.append(current.strip())
            current = ""
            i += 1
            continue
        if char in "&|" and i + 1 < len(bash_command) and bash_command[i + 1] == char:
            if current.strip():
                segments.append(current.strip())
            current = ""
            i += 2
            continue
        if char == "|" and (i + 1 >= len(bash_command) or bash_command[i + 1] != "|"):
            if current.strip():
                segments.append(current.strip())
            current = ""
            i += 1
            continue
        current += char
        i += 1

    if current.strip():
        segments.append(current.strip())

    commands = []
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
            if tokens:
                cmd = tokens[0]
                while "=" in cmd and len(tokens) > 1:
                    tokens = tokens[1:]
                    cmd = tokens[0] if tokens else ""
                if cmd:
                    commands.append(cmd.split("/")[-1])
        except ValueError:
            match = re.match(r"(\S+)", segment)
            if match:
                commands.append(match.group(1).split("/")[-1])

    return commands


def validate_bash_command(command: str) -> tuple[bool, str]:
    """Validate bash command against allowlist with enhanced security checks."""
    commands = extract_commands(command)

    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return False, f"Command '{cmd}' not allowed"

    # Enhanced rm validation - check for recursive deletion
    if "rm" in commands:
        # Match rm with -r, -R, --recursive, -f, --force flags (must be space-prefixed)
        rm_dangerous = re.search(r'\brm\b[^;&|]*(\s-[rRf]|\s--recursive|\s--force)', command)
        if rm_dangerous:
            safe_dirs = ["node_modules", "__pycache__", ".venv", "dist", "build", ".next", ".turbo"]
            # Extract paths after rm command (skip flags)
            # Find the rm segment and extract non-flag arguments
            rm_segment = re.search(r'\brm\b([^;&|]*)', command)
            if rm_segment:
                rm_args = rm_segment.group(1)
                # Split by whitespace and filter out flags (starting with -)
                parts = rm_args.split()
                targets = [p for p in parts if p and not p.startswith('-')]

                if not targets:
                    return False, "rm with recursive/force flags requires explicit target"

                for target in targets:
                    target_clean = target.rstrip('/')
                    # Check if target is a safe directory
                    is_safe = any(
                        target_clean == d or
                        target_clean == f"./{d}" or
                        target_clean.endswith(f"/{d}")
                        for d in safe_dirs
                    )
                    if not is_safe:
                        return False, f"rm with recursive/force flags only allowed for: {', '.join(safe_dirs)}"

    # Enhanced kill/pkill validation - require process name as primary argument
    if "kill" in commands or "pkill" in commands:
        allowed_targets = ["node", "npm", "pnpm", "vite", "modal", "uvicorn", "python", "tsc"]
        # For pkill, the pattern should be a dev process
        if "pkill" in commands:
            pkill_match = re.search(r'\bpkill\b[^;&|]*?([^\s-][^\s]*)\s*$', command)
            if not pkill_match or not any(t in pkill_match.group(1) for t in allowed_targets):
                return False, f"pkill only allowed for: {', '.join(allowed_targets)}"
        # For kill, only allow with signal + dev process name patterns
        if "kill" in commands and "pkill" not in commands:
            # kill should typically be used with pkill pattern or specific known PIDs
            # Block arbitrary PID killing
            if re.search(r'\bkill\b[^;&|]*\d+', command):
                return False, "kill with arbitrary PIDs not allowed; use pkill with process names"

    # Block curl/wget piping to interpreters
    if "curl" in commands or "wget" in commands:
        if re.search(r'(curl|wget)[^|]*\|\s*(python|python3|node|bash|sh|perl|ruby)', command):
            return False, "Piping downloaded content to interpreters not allowed"

    # Block downloading and executing in sequence
    if ("curl" in commands or "wget" in commands) and ("python" in commands or "python3" in commands or "node" in commands):
        # Check for download-then-execute patterns
        has_download = re.search(r'(curl|wget)[^;&|]*(\.py|\.js|\.sh)', command)
        has_execute = re.search(r'(python|python3|node)\s+\S*\.(py|js)', command)
        if has_download and has_execute:
            return False, "Downloading and executing scripts not allowed"

    return True, ""


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
# Tool Implementations
# =============================================================================

def execute_bash(command: str, cwd: Path) -> tuple[str, int]:
    """Execute bash command with security validation."""
    is_valid, error = validate_bash_command(command)
    if not is_valid:
        return f"BLOCKED: {error}", 1

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        return output[:10000] if len(output) > 10000 else output, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out (120s)", 1
    except Exception as e:
        return f"Error: {e}", 1


def read_file(file_path: str, cwd: Path) -> str:
    """Read file from project directory."""
    full_path = cwd / file_path
    if not full_path.exists():
        return f"File not found: {file_path}"
    try:
        content = full_path.read_text()
        return content[:50000] if len(content) > 50000 else content
    except Exception as e:
        return f"Error: {e}"


def write_file(file_path: str, content: str, cwd: Path) -> str:
    """Write file to project directory."""
    full_path = cwd / file_path

    try:
        full_path.resolve().relative_to(cwd.resolve())
    except ValueError:
        return "Error: Cannot write outside project directory"

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return f"Wrote {file_path}"
    except Exception as e:
        return f"Error: {e}"


def list_files(directory: str, cwd: Path) -> str:
    """List files in project directory."""
    full_path = cwd / directory if directory else cwd
    try:
        files = []
        skip = {"node_modules", ".venv", "__pycache__", ".git", "dist"}
        for item in full_path.rglob("*"):
            if item.is_file():
                rel = item.relative_to(cwd)
                if not any(p in rel.parts for p in skip):
                    files.append(str(rel))
        return "\n".join(sorted(files)[:500])
    except Exception as e:
        return f"Error: {e}"


TOOLS = [
    {
        "name": "bash",
        "description": "Execute bash command. Use for git, npm/pnpm, dev servers, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Bash command to execute"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file from the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to project root"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to project root"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "List project files (excludes node_modules, .venv, etc).",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Subdirectory (optional)"}
            }
        }
    },
]


def handle_tool(name: str, input: dict, cwd: Path) -> str:
    """Handle tool call from Claude."""
    if name == "bash":
        output, code = execute_bash(input["command"], cwd)
        return f"Exit code: {code}\n{output}"
    elif name == "read_file":
        return read_file(input["path"], cwd)
    elif name == "write_file":
        return write_file(input["path"], input["content"], cwd)
    elif name == "list_files":
        return list_files(input.get("directory", ""), cwd)
    return f"Unknown tool: {name}"


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
- Start dev servers: `./init.sh` or manually
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

1. Start dev servers:
   - Frontend: `cd frontend && pnpm run dev` (http://localhost:5173)
   - Backend: `cd backend && modal serve modal_app.py`
2. Verify the feature works per its `steps` array
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


async def run_session_api(
    project_dir: Path,
    is_initializer: bool = False,
) -> tuple[Literal["continue", "complete", "error"], str]:
    """Run a session using direct Anthropic API."""
    from anthropic import Anthropic

    client = Anthropic()
    model = get_model(is_initializer)
    user_prompt = load_prompt(project_dir, is_initializer)
    messages = [{"role": "user", "content": user_prompt}]

    print(f"   Model: {model}")

    while True:
        print("\n🤖 Thinking...")

        try:
            response = client.messages.create(
                model=model,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except Exception as e:
            return "error", f"API error: {e}"

        assistant_content = []
        tool_results = []

        for block in response.content:
            if block.type == "text":
                text = block.text
                print(f"\n{text[:2000]}{'...' if len(text) > 2000 else ''}")
                assistant_content.append(block)
            elif block.type == "tool_use":
                print(f"\n🔧 {block.name}")
                if block.name == "bash":
                    print(f"   $ {block.input.get('command', '')[:100]}")

                result = handle_tool(block.name, block.input, project_dir)
                print(f"   → {result[:200]}{'...' if len(result) > 200 else ''}")

                assistant_content.append(block)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if tool_results:
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
        else:
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return "continue", final_text


def run_session_claude_code(
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


async def run_agent(
    project_dir: Path,
    max_iterations: int | None = None,
    use_claude_code: bool = False,
):
    """Run the autonomous coding agent."""
    project_dir = project_dir.resolve()

    print(f"\n📁 Project: {project_dir}")
    if use_claude_code:
        print("🤖 Mode: Claude Code CLI (uses your existing authentication)")
    else:
        init_model = get_model(is_initializer=True)
        coding_model = get_model(is_initializer=False)
        if init_model == coding_model:
            print(f"🤖 Mode: API (model: {init_model})")
        else:
            print(f"🤖 Mode: API (init: {init_model}, coding: {coding_model})")

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

        # Run session with appropriate backend
        if use_claude_code:
            status, response = run_session_claude_code(project_dir, is_initializer)
        else:
            status, response = await run_session_api(project_dir, is_initializer)

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
            await asyncio.sleep(DELAY_BETWEEN_SESSIONS)


def main():
    parser = argparse.ArgumentParser(
        description="FastReact Autonomous Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  By default, auto-detects the best available mode:
  1. If Claude Code CLI is installed → uses Claude Code (no extra cost)
  2. If ANTHROPIC_API_KEY is set → uses direct API
  3. Otherwise → shows setup instructions

  You can also force a specific mode:
  --claude-code  Force Claude Code mode (requires 'claude' CLI)
  --api          Force API mode (requires ANTHROPIC_API_KEY)

Environment Variables (API mode only):
  ANTHROPIC_API_KEY           API key for direct API access
  FASTREACT_INITIALIZER_MODEL Model for initializer (default: claude-opus-4-5-20251101)
  FASTREACT_CODING_MODEL      Model for coding (default: claude-opus-4-5-20251101)

  Note: Model env vars are ignored in Claude Code mode.

Examples:
  uv run agent                    # Auto-detect mode
  uv run agent --claude-code      # Use Claude Code (model managed by Claude Code)

  # Use Sonnet for coding to save costs (API mode only):
  FASTREACT_CODING_MODEL=claude-sonnet-4-5-20250929 uv run agent --api
        """,
    )
    parser.add_argument("--max-iterations", type=int, help="Max iterations")
    parser.add_argument("--api", action="store_true", help="Force API mode")
    parser.add_argument("--claude-code", action="store_true", help="Force Claude Code mode")
    args = parser.parse_args()

    # Determine which mode to use
    use_claude_code = False

    if args.api and args.claude_code:
        print("❌ Cannot use both --api and --claude-code")
        sys.exit(1)

    if args.claude_code:
        # Force Claude Code mode
        if not has_claude_code():
            print("❌ Claude Code CLI not found")
            print("\nInstall: https://docs.anthropic.com/en/docs/claude-code")
            sys.exit(1)
        use_claude_code = True
    elif args.api:
        # Force API mode
        if not has_api_key():
            print("❌ ANTHROPIC_API_KEY not set")
            print("\nGet your key: https://console.anthropic.com/")
            print("Then: export ANTHROPIC_API_KEY='sk-...'")
            sys.exit(1)
        use_claude_code = False
    else:
        # Auto-detect: prefer Claude Code (already paid), fall back to API key
        if has_claude_code():
            use_claude_code = True
            print("📡 Using Claude Code (existing subscription)")
        elif has_api_key():
            use_claude_code = False
            print("📡 Using API mode (ANTHROPIC_API_KEY found)")
        else:
            print("❌ No authentication method found")
            print("\nOption 1: Install Claude Code (recommended)")
            print("  https://docs.anthropic.com/en/docs/claude-code")
            print("\nOption 2: Set ANTHROPIC_API_KEY")
            print("  export ANTHROPIC_API_KEY='sk-...'")
            print("  Get your key: https://console.anthropic.com/")
            sys.exit(1)

    # Project is parent of agent/
    project_dir = Path(__file__).parent.parent

    try:
        asyncio.run(run_agent(
            project_dir,
            max_iterations=args.max_iterations,
            use_claude_code=use_claude_code,
        ))
    except KeyboardInterrupt:
        print("\n\n⏸️  Paused. Resume with: uv run agent")


if __name__ == "__main__":
    main()
