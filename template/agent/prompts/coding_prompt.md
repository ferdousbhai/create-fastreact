# Coding Session

Continue implementing the application from feature_list.json.

## Step 1: Orient Yourself (MANDATORY)

Start by reading these files to understand the project state:

```bash
# 1. Check current progress
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'

# 2. Read previous session notes
cat claude-progress.txt

# 3. See recent changes
git log --oneline -5

# 4. Understand the app requirements
cat app_spec.md
```

## Step 2: Verify Before Building

If there are passing features, verify 1-2 core ones still work:
- Run `pnpm run dev` from project root
- Test a key user flow through the UI
- If anything is broken, fix it BEFORE new work

## Step 3: Select Next Feature

Find the first feature where `"passes": false` in feature_list.json.
This is your focus for this session.

## Step 4: Implement the Feature

Write code in:
- `frontend/` - React 19 + TypeScript + Tailwind v4 + shadcn/ui
- `backend/` - FastAPI on Modal

Add UI components:
```bash
cd frontend && pnpm dlx shadcn@latest add <component-name>
```

## Step 5: Test Thoroughly

1. Run `pnpm run dev` from project root (if not running)
2. Verify the feature works per its `steps` array at http://localhost:5173
3. Check browser console for errors
4. Test edge cases

## Step 6: Mark Complete

Update `feature_list.json`:
```json
"passes": true
```

ONLY change the `passes` field - NEVER edit descriptions or steps.

## Step 7: Commit

```bash
git add -A
git commit -m "feat: <description>"
```

## Step 8: Update Progress Notes

Append a session entry to `claude-progress.txt`:

```
### Session [N] - [Date]
**Progress:** X/Y features passing

**Completed:**
- Feature: <name> - <brief description of implementation>

**Issues Encountered:**
- <any blockers or problems>

**Next Session Should:**
- <specific next steps>
- <any warnings or gotchas>
```

This context helps the next session pick up where you left off.

## Rules

1. **ONE feature per session** - Complete and commit before moving on
2. **Test before marking complete** - Verify through the actual UI
3. **Leave codebase working** - No broken features when you exit
4. **Document your work** - claude-progress.txt is the handoff to the next session
5. **If blocked** - Document the issue clearly and move to the next feature
