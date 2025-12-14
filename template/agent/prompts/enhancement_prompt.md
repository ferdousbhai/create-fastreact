# Enhancement Session

You are adding NEW features to an EXISTING FastReact project.

## Step 1: Understand Current State

```bash
pwd && ls -la
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'
cat feature_list.json
cat claude-progress.txt
git log --oneline -20
```

## Step 2: Read New Requirements

Read `app_spec.md` for new features. Verify Modal auth: `modal token show`

## Step 3: Check for New Secrets

If new features need additional secrets:

```bash
modal secret list | grep <project-name>-secrets
```

Tell user to update: `modal secret create <project-name>-secrets EXISTING="..." NEW_KEY="..."` (replaces entire secret, include all values). **STOP and wait for confirmation.**

## Step 4: Append New Features

**CRITICAL: PRESERVE all existing features!** APPEND new features to the end of `feature_list.json`.

**NEVER** remove, modify, reorder existing features, or reset `"passes": true` to false.

```json
{ "category": "backend-api", "description": "...", "steps": ["..."], "passes": false }
```

**Categories:** `backend-api`, `frontend-ui`, `state`, `auth`, `styling`, `integration`

## Step 5: Document and Commit

Update `app_spec.md` with new requirements if needed. Update `claude-progress.txt` with new features added.

```bash
git add -A && git commit -m "feat: add new features to feature_list.json"
```

---

**IMPORTANT**: Do NOT implement features yet - just update feature list and docs.
