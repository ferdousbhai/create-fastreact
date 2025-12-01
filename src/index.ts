#!/usr/bin/env node

import { execSync } from "node:child_process";
import prompts from "prompts";
import pc from "picocolors";
import open from "open";
import { createProject } from "./create.js";

const banner = `
  ${pc.cyan("╭─────────────────────────────────────────╮")}
  ${pc.cyan("│")}                                         ${pc.cyan("│")}
  ${pc.cyan("│")}   ${pc.bold("fastreact")}                             ${pc.cyan("│")}
  ${pc.cyan("│")}   ${pc.dim("React + FastAPI + Modal")}               ${pc.cyan("│")}
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

function getModalUsername(): string | null {
  try {
    const username = execSync("modal profile current", { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
    return username || null;
  } catch {
    return null;
  }
}

async function main() {
  console.log(banner);

  // Auto-detect Modal username
  const detectedUsername = getModalUsername();
  if (detectedUsername) {
    console.log(pc.dim(`  Detected Modal username: ${pc.cyan(detectedUsername)}`));
    console.log();
  }

  const response = await prompts([
    {
      type: "text",
      name: "projectName",
      message: "Project name:",
      initial: "my-app",
      validate: validateProjectName,
    },
    {
      type: "text",
      name: "modalUsername",
      message: "Modal username:",
      initial: detectedUsername || "",
      validate: (value) => value ? true : "Modal username is required",
    },
    {
      type: "confirm",
      name: "configureAuth",
      message: "Configure proxy auth tokens now? (can add later for production)",
      initial: false,
    },
  ]);

  if (!response.projectName || !response.modalUsername) {
    console.log(pc.red("\nOperation cancelled."));
    process.exit(1);
  }

  let modalKey = "";
  let modalSecret = "";

  if (response.configureAuth) {
    console.log();
    console.log(pc.dim("  Opening Modal proxy auth token page..."));
    await open("https://modal.com/settings/proxy-auth-tokens");
    console.log(pc.dim("  Create a new token and paste the values below."));
    console.log();

    const authResponse = await prompts([
      {
        type: "text",
        name: "modalKey",
        message: "Modal proxy auth token ID (wk-xxx):",
        validate: (value) => value ? true : "Token ID is required (or go back and skip auth)",
      },
      {
        type: "password",
        name: "modalSecret",
        message: "Modal proxy auth token secret (ws-xxx):",
        validate: (value) => value ? true : "Token secret is required (or go back and skip auth)",
      },
    ]);

    if (!authResponse.modalKey || !authResponse.modalSecret) {
      console.log(pc.yellow("\nSkipping proxy auth configuration."));
    } else {
      modalKey = authResponse.modalKey;
      modalSecret = authResponse.modalSecret;
    }
  }

  try {
    await createProject({
      projectName: response.projectName,
      modalUsername: response.modalUsername,
      modalKey,
      modalSecret,
    });

    if (!modalKey) {
      console.log(pc.yellow("Note:"), "Proxy auth not configured. Your API is publicly accessible.");
      console.log(pc.dim("      Add auth tokens later in frontend/.env.local for production."));
      console.log();
    }
  } catch (error) {
    console.error(pc.red("\nError:"), error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
