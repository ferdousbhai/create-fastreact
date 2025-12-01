import { existsSync, readdirSync, mkdirSync, copyFileSync, readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import pc from "picocolors";

const __dirname = dirname(fileURLToPath(import.meta.url));

interface ProjectConfig {
  projectName: string;
  modalUsername: string;
  modalKey: string;
  modalSecret: string;
}

export async function createProject(config: ProjectConfig) {
  const { projectName, modalUsername, modalKey, modalSecret } = config;
  const targetDir = join(process.cwd(), projectName);

  // Check if directory exists and is not empty
  if (existsSync(targetDir)) {
    const files = readdirSync(targetDir);
    if (files.length > 0) {
      throw new Error(`Directory "${projectName}" already exists and is not empty.`);
    }
  }

  console.log();
  console.log(`Creating project in ${pc.cyan(targetDir)}...`);

  // Find template directory (relative to dist or src)
  let templateDir = join(__dirname, "..", "template");
  if (!existsSync(templateDir)) {
    templateDir = join(__dirname, "..", "..", "template");
  }
  if (!existsSync(templateDir)) {
    throw new Error("Could not find template directory");
  }

  // Copy template files
  mkdirSync(targetDir, { recursive: true });
  copyDir(templateDir, targetDir, projectName);

  // Generate Modal URLs
  const devApiUrl = `https://${modalUsername}--${projectName}-backend-fastapi-app-dev.modal.run`;
  const prodApiUrl = `https://${modalUsername}--${projectName}-backend-fastapi-app.modal.run`;

  // Write frontend/.env.local with Modal config
  const authSection = modalKey && modalSecret
    ? `VITE_MODAL_KEY=${modalKey}
VITE_MODAL_SECRET=${modalSecret}`
    : `# Proxy auth not configured - API is publicly accessible
# Add these for production security:
# VITE_MODAL_KEY=wk-xxx
# VITE_MODAL_SECRET=ws-xxx`;

  const envLocalContent = `# Modal API Configuration (Development)
VITE_API_URL=${devApiUrl}
${authSection}

# Production URL (for reference, configure in Vercel)
# VITE_API_URL=${prodApiUrl}
`;
  writeFileSync(join(targetDir, "frontend", ".env.local"), envLocalContent);

  // Initialize git
  console.log(pc.dim("  Initializing git repository..."));
  try {
    execSync("git init", { cwd: targetDir, stdio: "ignore" });
    execSync("git add -A", { cwd: targetDir, stdio: "ignore" });
  } catch {
    // Git not available, skip
  }

  // Install root dependencies (concurrently)
  console.log(pc.dim("  Installing dependencies..."));
  try {
    execSync("pnpm install", { cwd: targetDir, stdio: "ignore" });
  } catch {
    console.log(pc.yellow("  Warning: Could not install root dependencies. Run 'pnpm install' manually."));
  }

  // Install frontend dependencies
  console.log(pc.dim("  Installing frontend dependencies..."));
  try {
    execSync("pnpm install", { cwd: join(targetDir, "frontend"), stdio: "ignore" });
  } catch {
    console.log(pc.yellow("  Warning: Could not install frontend dependencies. Run 'pnpm install' in frontend/ manually."));
  }

  // Install backend dependencies
  console.log(pc.dim("  Installing backend dependencies..."));
  try {
    execSync("uv sync", { cwd: join(targetDir, "backend"), stdio: "ignore" });
  } catch {
    console.log(pc.yellow("  Warning: Could not install backend dependencies. Run 'uv sync' in backend/ manually."));
  }

  // Success message
  console.log();
  console.log(pc.green("✔"), `Created ${pc.bold(projectName)}`);
  console.log();
  console.log("Next steps:");
  console.log(pc.cyan(`  cd ${projectName}`));
  console.log(pc.cyan("  pnpm run dev"));
  console.log();
  console.log(`Frontend: ${pc.dim("http://localhost:5173")}`);
  console.log(`Backend:  ${pc.dim(devApiUrl)}`);
  console.log();
}

function copyDir(src: string, dest: string, projectName: string) {
  mkdirSync(dest, { recursive: true });

  const entries = readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = join(src, entry.name);
    let destPath = join(dest, entry.name);

    // Skip node_modules, .venv, __pycache__, etc.
    if (["node_modules", ".venv", "__pycache__", ".git", "pnpm-lock.yaml", "uv.lock"].includes(entry.name)) {
      continue;
    }

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath, projectName);
    } else {
      // Rename gitignore to .gitignore (npm strips .gitignore files during publish)
      if (entry.name === "gitignore") {
        destPath = join(dest, ".gitignore");
      }

      // Handle .hbs template files
      if (entry.name.endsWith(".hbs")) {
        destPath = destPath.slice(0, -4); // Remove .hbs extension
        let content = readFileSync(srcPath, "utf-8");
        content = content.replace(/\{\{projectName\}\}/g, projectName);
        content = content.replace(/\{\{projectNamePascal\}\}/g, toPascalCase(projectName));
        writeFileSync(destPath, content);
      } else {
        copyFileSync(srcPath, destPath);
      }
    }
  }
}

function toPascalCase(str: string): string {
  return str
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join("");
}
