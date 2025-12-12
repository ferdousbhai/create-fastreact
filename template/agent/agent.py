#!/usr/bin/env python3
"""
FastReact Autonomous Coding Agent
=================================

Two-phase autonomous coding agent:
1. Initializer: Reads instructions and generates/updates feature_list.json
2. Coder: Implements features from feature_list.json incrementally

Commands:
  uv run agent [INSTRUCTIONS]  # Run initializer + coding (reads app_spec.md or uses INSTRUCTIONS)
  uv run agent --continue      # Skip initializer, only code existing features

Runs via Claude Code CLI using your existing Claude Code authentication.

Based on Anthropic's autonomous-coding architecture:
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
"""

import argparse
import json
import select
import subprocess
import sys
import termios
import time
import tty
from datetime import datetime
from pathlib import Path
from typing import Literal

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_TIMEOUT = 1200  # 20 minutes per session
DELAY_BETWEEN_SESSIONS = 3
LOGS_DIR = ".fastreact-agent/logs"


# =============================================================================
# CLI Detection
# =============================================================================

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
# Session Logging
# =============================================================================

def get_log_path(project_dir: Path, session_type: str) -> Path:
    """Get the log file path for a session."""
    logs_dir = project_dir / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return logs_dir / f"{timestamp}_{session_type}.log"


def write_session_log(
    log_path: Path,
    session_type: str,
    prompt: str,
    stdout: str,
    stderr: str,
    duration_seconds: float,
) -> None:
    """Write session output to a log file."""
    with open(log_path, "w") as f:
        f.write(f"Session Type: {session_type}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Duration: {duration_seconds:.1f}s\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write("PROMPT:\n")
        f.write("=" * 70 + "\n\n")
        f.write(prompt)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("STDOUT:\n")
        f.write("=" * 70 + "\n\n")
        f.write(stdout or "(empty)")
        if stderr:
            f.write("\n\n" + "=" * 70 + "\n")
            f.write("STDERR:\n")
            f.write("=" * 70 + "\n\n")
            f.write(stderr)


# =============================================================================
# Feature List Management & Validation
# =============================================================================

def load_feature_list(project_dir: Path) -> list | None:
    """Load feature_list.json from project directory."""
    feature_file = project_dir / "feature_list.json"
    if not feature_file.exists():
        return None
    try:
        with open(feature_file) as f:
            data = json.load(f)
            # Normalize nested format to flat array
            if isinstance(data, dict) and "categories" in data:
                features = []
                for category in data.get("categories", []):
                    for feature in category.get("features", []):
                        features.append(feature)
                return features
            return data if isinstance(data, list) else None
    except (json.JSONDecodeError, IOError):
        return None


def save_feature_list(project_dir: Path, features: list) -> None:
    """Save features back to feature_list.json."""
    feature_file = project_dir / "feature_list.json"
    feature_file.write_text(json.dumps(features, indent=2))


def validate_feature_changes(
    before: list | None, after: list | None, allow_additions: bool = True
) -> tuple[bool, str]:
    """
    Validate that feature_list.json changes follow the rules:
    - Features cannot be removed
    - Feature descriptions cannot be modified
    - New features can only be added if allow_additions=True

    Returns (is_valid, error_message).
    """
    if before is None:
        return True, ""  # First creation is always valid

    if after is None:
        return False, "feature_list.json was deleted or corrupted"

    # Check for removed features (description changed = feature removed + new one added)
    before_descriptions = {f.get("description", "") for f in before}
    after_descriptions = {f.get("description", "") for f in after}
    removed = before_descriptions - after_descriptions

    if removed:
        # Truncate long descriptions in error message
        removed_short = {d[:60] + "..." if len(d) > 60 else d for d in removed}
        return False, f"Features were removed or modified: {removed_short}"

    # Check for additions when not allowed
    if not allow_additions:
        added = after_descriptions - before_descriptions
        if added:
            added_short = {d[:60] + "..." if len(d) > 60 else d for d in added}
            return False, f"New features added in --continue mode: {added_short}"

    return True, ""


def count_passing_features(project_dir: Path) -> tuple[int, int]:
    """Count passing features from feature_list.json."""
    features = load_feature_list(project_dir)
    if not features:
        return 0, 0

    total = len(features)
    passing = sum(1 for f in features if f.get("passes", False))
    return passing, total


def is_project_complete(project_dir: Path) -> bool:
    """Check if all features in feature_list.json are passing."""
    passing, total = count_passing_features(project_dir)
    return total > 0 and passing == total


# =============================================================================
# Progress Display
# =============================================================================

def print_progress(project_dir: Path) -> None:
    """Print progress bar."""
    passing, total = count_passing_features(project_dir)

    if total == 0:
        print("  No feature_list.json found yet")
        return

    pct = (passing / total) * 100
    bar_len = 30
    filled = int(bar_len * passing / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  Progress: [{bar}] {passing}/{total} ({pct:.1f}%)")


def print_session_header(session: int, session_type: str) -> None:
    """Print session header."""
    print(f"\n{'='*60}")
    print(f"SESSION {session}: {session_type.upper()}")
    print("=" * 60)


def print_session_result(
    newly_completed: list,
    prev_passing: int,
    duration: float,
    total_time: float,
) -> None:
    """Print session completion summary."""
    if newly_completed:
        print(f"\n  Completed this session:")
        for f in newly_completed[:3]:  # Show max 3
            desc = f.get("description", "Unknown")[:50]
            print(f"    + {desc}")
        if len(newly_completed) > 3:
            print(f"    + ...and {len(newly_completed) - 3} more")

    print(f"\n  Session duration: {duration:.0f}s | Total runtime: {total_time:.0f}s")


# =============================================================================
# Stop Signal Handling
# =============================================================================

def wait_for_stop_signal(timeout: float = 3.0) -> bool:
    """
    Wait for user keypress to stop between sessions.
    Returns True if user wants to stop, False to continue.
    """
    print(f"\n  Press any key to pause, or wait {timeout:.0f}s to continue...", end="", flush=True)

    try:
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Set terminal to raw mode for single keypress detection
            tty.setcbreak(sys.stdin.fileno())

            # Use select to wait for input with timeout
            ready, _, _ = select.select([sys.stdin], [], [], timeout)

            if ready:
                sys.stdin.read(1)  # Consume the keypress
                print(" [PAUSED]")
                return True
            else:
                print(" [CONTINUING]")
                return False
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except (termios.error, AttributeError):
        # Fallback for non-TTY environments
        time.sleep(timeout)
        return False


# =============================================================================
# Prompts
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


def load_prompt(project_dir: Path, prompt_name: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_file = project_dir / "agent" / "prompts" / f"{prompt_name}.md"
    if prompt_file.exists():
        return prompt_file.read_text()
    return ""


# =============================================================================
# Agent Session
# =============================================================================

def run_session(
    project_dir: Path,
    prompt: str,
    session_type: str = "coding",
    timeout: int = DEFAULT_TIMEOUT,
    verbose: bool = False,
) -> tuple[Literal["continue", "complete", "error"], str, float]:
    """
    Run a session using Claude Code CLI.
    Returns (status, output, duration_seconds).
    """
    full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\n{prompt}"
    log_path = get_log_path(project_dir, session_type)
    start_time = time.time()

    if verbose:
        print(f"\n  Running {session_type} session (verbose mode)...\n")
    else:
        print(f"\n  Running {session_type} session...")

    try:
        if verbose:
            # Stream output in real-time
            process = subprocess.Popen(
                [
                    "claude",
                    "--print",
                    "--dangerously-skip-permissions",
                    "-p", full_prompt,
                ],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(f"    {line.rstrip()}")
                    stdout_lines.append(line)

            stderr = process.stderr.read()
            stdout = "".join(stdout_lines)
            returncode = process.returncode
        else:
            # Capture output with spinner indication
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
                timeout=timeout,
            )
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode

        duration = time.time() - start_time

        # Log the session
        write_session_log(log_path, session_type, full_prompt, stdout, stderr, duration)

        if returncode != 0:
            return "error", f"Claude Code error: {stderr}", duration

        # Print truncated output in non-verbose mode
        if not verbose and stdout:
            preview = stdout[:1500]
            if len(stdout) > 1500:
                preview += f"\n\n... [{len(stdout) - 1500} more chars, see {log_path.name}]"
            print(f"\n{preview}")

        return "continue", stdout, duration

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        write_session_log(log_path, session_type, full_prompt, "", f"TIMEOUT after {timeout}s", duration)
        return "error", f"Session timed out ({timeout}s)", duration
    except Exception as e:
        duration = time.time() - start_time
        write_session_log(log_path, session_type, full_prompt, "", str(e), duration)
        return "error", f"Claude Code error: {e}", duration


# =============================================================================
# Main Agent Loop
# =============================================================================

def get_or_create_app_spec(project_dir: Path, cli_instructions: str | None) -> str | None:
    """
    Get instructions from app_spec.md, or create it from CLI instructions.
    Returns None if no instructions available.
    """
    app_spec_file = project_dir / "app_spec.md"

    # If CLI instructions provided, create/update app_spec.md
    if cli_instructions:
        app_spec_content = f"# App Specification\n\n{cli_instructions}\n"
        app_spec_file.write_text(app_spec_content)
        print(f"  Created app_spec.md from instructions")
        return cli_instructions

    # Otherwise read from existing file
    if app_spec_file.exists():
        return app_spec_file.read_text()

    return None


def run_agent(
    project_dir: Path,
    instructions: str | None = None,
    continue_mode: bool = False,
    max_iterations: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    verbose: bool = False,
):
    """
    Run the autonomous coding agent.

    Args:
        project_dir: Path to the project root
        instructions: App instructions (from CLI or app_spec.md)
        continue_mode: If True, skip initializer and only code existing features
        max_iterations: Maximum number of sessions to run
        timeout: Timeout per session in seconds
        verbose: Stream output in real-time
    """
    project_dir = project_dir.resolve()

    print(f"\n  Project: {project_dir}")
    print(f"  Mode: {'Continue (existing features only)' if continue_mode else 'Full (initializer + coding)'}")
    print(f"  Timeout: {timeout}s per session")
    if verbose:
        print("  Output: Verbose (streaming)")

    # Check feature_list.json for --continue mode
    feature_list_exists = (project_dir / "feature_list.json").exists()

    if continue_mode:
        if not feature_list_exists:
            print("\n  Error: Cannot use --continue without existing feature_list.json")
            print("  Run 'uv run agent' first to initialize the feature list.")
            sys.exit(1)
        print("\n  Continuing: Working on existing features only")
        skip_initializer = True
    else:
        # Need instructions for initializer
        if not instructions:
            print("\n  Error: No instructions provided!")
            print("  Either create app_spec.md or run: uv run agent \"Your app description\"")
            sys.exit(1)

        if feature_list_exists:
            print("\n  Existing project: Running initializer (may add new features)")
        else:
            print("\n  New project: Running initializer to create feature list")
        skip_initializer = False

    session = 1
    iteration = 0
    total_run_time = 0.0
    initializer_done = skip_initializer  # Skip if --continue mode

    while True:
        if max_iterations and iteration >= max_iterations:
            print(f"\n  Max iterations reached ({max_iterations})")
            break

        # Determine which prompt to use
        if not initializer_done:
            prompt_template = load_prompt(project_dir, "initializer_prompt")
            # Inject instructions into the initializer prompt
            prompt = f"{prompt_template}\n\n## App Instructions\n\n{instructions}"
            session_type = "initializer"
        else:
            prompt = load_prompt(project_dir, "coding_prompt")
            session_type = "coding"

        if not prompt:
            print(f"\n  Error: Could not load {session_type} prompt")
            sys.exit(1)

        print_session_header(session, session_type)
        print_progress(project_dir)

        # Snapshot features before session
        features_before = load_feature_list(project_dir)
        prev_passing = sum(1 for f in (features_before or []) if f.get("passes"))

        # Run the session
        status, response, duration = run_session(
            project_dir, prompt, session_type, timeout, verbose
        )
        total_run_time += duration

        print(f"\n  Session result: {status}")

        # Validate feature_list.json changes
        # In --continue mode, don't allow new features to be added
        features_after = load_feature_list(project_dir)
        is_valid, error = validate_feature_changes(
            features_before,
            features_after,
            allow_additions=not continue_mode
        )

        if not is_valid:
            print(f"\n  WARNING: Invalid feature_list.json change: {error}")
            if features_before is not None:
                print("  Restoring previous feature_list.json")
                save_feature_list(project_dir, features_before)
                features_after = features_before

        # Find newly completed features
        before_passing = {f.get("description") for f in (features_before or []) if f.get("passes")}
        newly_completed = [
            f for f in (features_after or [])
            if f.get("passes") and f.get("description") not in before_passing
        ]

        print_session_result(newly_completed, prev_passing, duration, total_run_time)

        # After initializer, check that feature_list.json was created
        if session_type == "initializer":
            if (project_dir / "feature_list.json").exists():
                print("\n  feature_list.json created/updated!")
                initializer_done = True
            else:
                print("\n  WARNING: feature_list.json not created - will retry")

        # Check if complete
        if is_project_complete(project_dir):
            passing, total = count_passing_features(project_dir)
            print(f"\n{'='*60}")
            print(f"  PROJECT COMPLETE!")
            print(f"  All {total} features passing")
            print(f"  Total sessions: {session}")
            print(f"  Total runtime: {total_run_time:.0f}s")
            print("=" * 60)
            break

        if status == "error":
            print(f"\n  Error: {response}")

        session += 1
        iteration += 1

        # Check for stop signal between sessions
        if max_iterations is None or iteration < max_iterations:
            if wait_for_stop_signal(DELAY_BETWEEN_SESSIONS):
                print(f"\n  Paused after session {session - 1}")
                print(f"  Resume with: uv run agent --continue")
                return


def main():
    parser = argparse.ArgumentParser(
        description="FastReact Autonomous Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  uv run agent [INSTRUCTIONS]  Run initializer + coding (uses app_spec.md or INSTRUCTIONS)
  uv run agent --continue      Skip initializer, only code existing features

Examples:
  uv run agent                              # Uses app_spec.md for instructions
  uv run agent "Build a todo app"           # Uses CLI argument for instructions
  uv run agent --continue                   # Resume coding existing features only
  uv run agent --continue -n 5              # Run at most 5 coding sessions
  uv run agent -v                           # Stream output in real-time
        """,
    )
    parser.add_argument(
        "instructions",
        nargs="?",
        default=None,
        help="App instructions (optional, defaults to reading app_spec.md)"
    )
    parser.add_argument(
        "--continue", "-c",
        dest="continue_mode",
        action="store_true",
        help="Continue mode: skip initializer, only code existing features"
    )
    parser.add_argument(
        "--max-iterations", "-n",
        type=int,
        help="Maximum number of sessions to run"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout per session in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream output in real-time instead of capturing"
    )
    args = parser.parse_args()

    # Check that Claude Code CLI is available
    if not has_claude_code():
        print("  Claude Code CLI not found")
        print("\n  Install Claude Code: https://docs.anthropic.com/en/docs/claude-code")
        sys.exit(1)

    # Project is parent of agent/
    project_dir = Path(__file__).parent.parent

    # Get instructions from CLI (creates app_spec.md) or read existing app_spec.md
    instructions = get_or_create_app_spec(project_dir, args.instructions)

    try:
        run_agent(
            project_dir,
            instructions=instructions,
            continue_mode=args.continue_mode,
            max_iterations=args.max_iterations,
            timeout=args.timeout,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Resume with: uv run agent --continue")


if __name__ == "__main__":
    main()
