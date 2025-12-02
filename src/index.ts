#!/usr/bin/env node

import { execSync, spawn, spawnSync } from "node:child_process";
import prompts from "prompts";
import pc from "picocolors";
import open from "open";
import { createProject } from "./create.js";

const banner = `
  ${pc.cyan("╭─────────────────────────────────────────╮")}
  ${pc.cyan("│")}                                         ${pc.cyan("│")}
  ${pc.cyan("│")}   ${pc.bold("fastreact")}                             ${pc.cyan("│")}
  ${pc.cyan("│")}   ${pc.dim("AI-First Full-Stack Framework")}         ${pc.cyan("│")}
  ${pc.cyan("│")}                                         ${pc.cyan("│")}
  ${pc.cyan("╰─────────────────────────────────────────╯")}
`;


function validateProjectName(name: string): string | true {
  if (!name) return "Project name is required";
  if (!/^[a-z0-9-]+$/.test(name)) {
    return "Project name can only contain lowercase letters, numbers, and hyphens";
  }
  return true;
}

// =============================================================================
// Modal CLI Setup
// =============================================================================

function isModalInstalled(): boolean {
  try {
    execSync("modal --version", { stdio: ["pipe", "pipe", "pipe"] });
    return true;
  } catch {
    return false;
  }
}

function getModalUsername(): string | null {
  try {
    const username = execSync("modal profile current", { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
    return username || null;
  } catch {
    return null;
  }
}

async function installModal(): Promise<boolean> {
  console.log(pc.dim("  Installing Modal CLI..."));

  const result = spawnSync("uv", ["tool", "install", "modal"], {
    stdio: "inherit",
  });

  if (result.status === 0) {
    console.log(pc.green("  ✔"), "Modal CLI installed");
    return true;
  } else {
    console.log(pc.red("  ✖"), "Failed to install Modal CLI");
    console.log(pc.dim("    Try manually: uv tool install modal"));
    return false;
  }
}

async function loginModal(): Promise<boolean> {
  console.log(pc.dim("  Opening browser for Modal login..."));
  console.log();

  const result = spawnSync("modal", ["setup"], {
    stdio: "inherit",
  });

  if (result.status === 0) {
    const username = getModalUsername();
    if (username) {
      console.log();
      console.log(pc.green("  ✔"), `Logged in as ${pc.cyan(username)}`);
      return true;
    }
  }

  console.log(pc.red("  ✖"), "Modal login failed");
  return false;
}

async function ensureModal(): Promise<string | null> {
  // Check if Modal is installed
  if (!isModalInstalled()) {
    console.log(pc.yellow("  ⚠"), "Modal CLI not found");
    console.log();

    const { install } = await prompts({
      type: "confirm",
      name: "install",
      message: "Install Modal CLI now?",
      initial: true,
    });

    if (!install) {
      console.log();
      console.log(pc.dim("  Modal is required for the backend."));
      console.log(pc.dim("  Install manually: uv tool install modal"));
      return null;
    }

    console.log();
    if (!await installModal()) {
      return null;
    }
    console.log();
  }

  // Check if logged in
  let username = getModalUsername();
  if (!username) {
    console.log(pc.yellow("  ⚠"), "Not logged in to Modal");
    console.log();

    const { login } = await prompts({
      type: "confirm",
      name: "login",
      message: "Log in to Modal now?",
      initial: true,
    });

    if (!login) {
      console.log();
      console.log(pc.dim("  Modal account required for the backend."));
      console.log(pc.dim("  Log in manually: modal setup"));
      return null;
    }

    console.log();
    if (!await loginModal()) {
      return null;
    }

    username = getModalUsername();
  }

  return username;
}

async function main() {
  console.log(banner);

  // Ensure Modal is installed and logged in
  const modalUsername = await ensureModal();
  if (!modalUsername) {
    console.log(pc.red("\nModal setup required. Exiting."));
    process.exit(1);
  }

  console.log(pc.dim(`  Modal username: ${pc.cyan(modalUsername)}`));
  console.log();

  // Step 1: Project name
  const { projectName } = await prompts({
    type: "text",
    name: "projectName",
    message: "Project name:",
    initial: "my-app",
    validate: validateProjectName,
  });

  if (!projectName) {
    console.log(pc.red("\nOperation cancelled."));
    process.exit(1);
  }

  // Step 2: App description in plain English
  console.log();
  const descResponse = await prompts({
    type: "text",
    name: "description",
    message: "Describe your app:",
    validate: (value) => value ? true : "Please describe what you want to build",
  });

  if (!descResponse.description) {
    console.log(pc.red("\nOperation cancelled."));
    process.exit(1);
  }

  const appDescription = descResponse.description;

  // Step 3: Modal auth (optional)
  console.log();
  const authResponse = await prompts({
    type: "confirm",
    name: "configureAuth",
    message: "Configure Modal proxy auth now? (can add later)",
    initial: false,
  });

  let modalKey = "";
  let modalSecret = "";

  if (authResponse.configureAuth) {
    console.log();
    console.log(pc.dim("  Opening Modal proxy auth token page..."));
    await open("https://modal.com/settings/proxy-auth-tokens");
    console.log(pc.dim("  Create a new token and paste the values below."));
    console.log();

    const tokenResponse = await prompts([
      {
        type: "text",
        name: "modalKey",
        message: "Modal proxy auth token ID (wk-xxx):",
      },
      {
        type: "password",
        name: "modalSecret",
        message: "Modal proxy auth token secret (ws-xxx):",
      },
    ]);

    modalKey = tokenResponse.modalKey || "";
    modalSecret = tokenResponse.modalSecret || "";
  }

  // Create the project
  try {
    await createProject({
      projectName,
      modalUsername,
      modalKey,
      modalSecret,
      appDescription,
    });

    // Summary
    console.log();
    console.log(pc.green("✔"), pc.bold("Project created!"));
    console.log();

    if (!modalKey) {
      console.log(pc.yellow("  Note:"), "Proxy auth not configured (API publicly accessible)");
      console.log();
    }

    // Next steps
    console.log(pc.bold("  Next steps:"));
    console.log();
    console.log(pc.cyan(`    cd ${projectName}/agent`));
    console.log(pc.cyan("    uv run agent"));
    console.log();
    console.log(pc.dim("  The agent auto-detects Claude Code or ANTHROPIC_API_KEY."));
    console.log(pc.dim("  Monitor progress in feature_list.json and claude-progress.txt"));
    console.log();

    // Ask if user wants to launch agent now
    const launchResponse = await prompts({
      type: "confirm",
      name: "launch",
      message: "Launch the AI agent now?",
      initial: true,
    });

    if (launchResponse.launch) {
      console.log();
      console.log(pc.dim("  Starting AI agent..."));
      console.log();

      const agentDir = `${process.cwd()}/${projectName}/agent`;
      const agent = spawn("uv", ["run", "agent"], {
        cwd: agentDir,
        stdio: "inherit",
        env: { ...process.env },
      });

      agent.on("error", (err) => {
        console.log(pc.red("  Failed to start agent:"), err.message);
        console.log(pc.dim(`  Run manually: cd ${projectName}/agent && uv run agent`));
      });
    }
  } catch (error) {
    console.error(pc.red("\nError:"), error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
