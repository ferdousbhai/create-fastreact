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
  appDescription: string;
}

function generateAppSpec(config: ProjectConfig): string {
  const { projectName, appDescription } = config;

  return `# ${projectName}

${appDescription}

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite for build tooling
- Tailwind CSS v4 for styling
- shadcn/ui for UI components (add with: \`pnpm dlx shadcn@latest add <component>\`)
- Path alias: \`@/\` maps to \`src/\`

### Backend
- FastAPI (Python 3.12)
- Modal for serverless deployment
- RESTful API design

## Project Structure

\`\`\`
${projectName}/
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── lib/        # Utilities and API client
│   │   ├── App.tsx     # Main app component
│   │   └── main.tsx    # Entry point
│   └── package.json
├── backend/            # FastAPI application
│   ├── app/
│   │   └── main.py     # FastAPI routes
│   └── modal_app.py    # Modal deployment config
├── agent/              # AI coding agent
│   └── agent.py        # Autonomous agent
├── app_spec.md         # This file
└── claude-progress.txt # AI session notes
\`\`\`

## Development

\`\`\`bash
# Frontend (http://localhost:5173)
cd frontend && pnpm run dev

# Backend (Modal dev server)
cd backend && modal serve modal_app.py

# Run AI agent
uv run agent
\`\`\`

## Guidelines for AI Agent

1. Read this spec carefully to understand what to build
2. Break down the app description into discrete features
3. Implement one feature at a time
4. Test each feature before moving on
5. Use shadcn/ui components for UI
6. Commit after each feature with descriptive messages
7. Update claude-progress.txt with session notes
`;
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

  // Generate app_spec.md
  console.log(pc.dim("  Generating app_spec.md..."));
  const appSpec = generateAppSpec(config);
  writeFileSync(join(targetDir, "app_spec.md"), appSpec);

  // Generate initial claude-progress.txt
  console.log(pc.dim("  Creating claude-progress.txt..."));
  const progressContent = `# ${projectName} - Development Progress

## App Description
${config.appDescription}

## Session Notes
(AI agent will append notes here after each session)

---
`;
  writeFileSync(join(targetDir, "claude-progress.txt"), progressContent);

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

  // Install agent dependencies
  console.log(pc.dim("  Installing agent dependencies..."));
  try {
    execSync("uv sync", { cwd: join(targetDir, "agent"), stdio: "ignore" });
  } catch {
    console.log(pc.yellow("  Warning: Could not install agent dependencies. Run 'uv sync' in agent/ manually."));
  }

  // Initial git commit
  console.log(pc.dim("  Creating initial commit..."));
  try {
    execSync("git add -A", { cwd: targetDir, stdio: "ignore" });
    execSync('git commit -m "Initial setup: FastReact project with AI agent"', { cwd: targetDir, stdio: "ignore" });
  } catch {
    // Git commit failed, skip
  }

  console.log();
  console.log(pc.green("✔"), `Scaffolded ${pc.bold(projectName)}`);
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
