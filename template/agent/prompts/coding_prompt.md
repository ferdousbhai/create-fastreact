# Coding Session

You are continuing work on a FastReact application. This is a FRESH context window - you have no memory of previous sessions.

## Step 1: Orient Yourself (MANDATORY)

Start by reading these files to understand the project state:

```bash
# 1. Your working directory
pwd
ls -la

# 2. Check current progress
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'

# 3. Read previous session notes
cat claude-progress.txt

# 4. See recent changes
git log --oneline -10

# 5. Understand the app requirements
cat app_spec.md
```

## Step 2: Start Servers (If Not Running)

Start backend first (runs on Modal with proxy auth):
```bash
cd backend && modal serve modal_app.py
```

**Capture the Modal URL** from output (e.g., `https://workspace--app-backend-fastapi-app-dev.modal.run`)

Check if `frontend/.env.local` has the correct configuration:
```bash
cat frontend/.env.local
```

The file should contain:
- `VITE_API_URL` - The Modal backend URL
- `VITE_MODAL_KEY` - Proxy auth token ID
- `VITE_MODAL_SECRET` - Proxy auth token secret

If the Modal URL changed (happens on restart), update it:
```bash
# Preserve existing auth keys, just update the URL
sed -i 's|VITE_API_URL=.*|VITE_API_URL=<new-modal-url>|' frontend/.env.local
```

Then start frontend:
```bash
cd frontend && pnpm run dev
```

**Troubleshooting auth errors:** If you see 401 errors in the browser console, verify the `VITE_MODAL_KEY` and `VITE_MODAL_SECRET` values in `.env.local` match the token created at https://modal.com/settings/proxy-auth-tokens

## Step 3: Verification Test (CRITICAL!)

**MANDATORY BEFORE NEW WORK:**

If there are features marked as `"passes": true`, verify 1-2 core ones still work.

**Test through the actual UI** at http://localhost:5173:
- Navigate to key pages
- Test primary user flows
- Check browser console for errors

**If you find ANY issues (functional or visual):**
- Mark that feature as `"passes": false` immediately
- Fix all issues BEFORE moving to new features
- This includes UI bugs like:
  * White-on-white text or poor contrast
  * Layout issues or overflow
  * Buttons too close together
  * Missing hover states
  * Console errors

**Note:** If this is the first coding session (no passing features), skip to Step 4.

## Step 4: Select Next Feature

Find the first feature where `"passes": false` in feature_list.json.
Focus on completing this ONE feature this session.

## Step 5: Implement the Feature

Write code in:
- `frontend/` - React 19 + TypeScript + Tailwind v4 + shadcn/ui
- `backend/` - FastAPI on Modal

Add UI components:
```bash
cd frontend && pnpm dlx shadcn@latest add <component-name>
```

### Recommended shadcn Components

- `button` - Primary actions
- `card` - Content containers
- `input` - Form fields
- `dialog` - Modals and confirmations
- `toast` - Notifications
- `form` - Form validation with react-hook-form

## Step 6: Verify with Browser Testing

**CRITICAL:** You MUST verify features through the actual UI.

- Test through the UI with clicks and keyboard input
- Check all states (loading, error, success)
- Verify complete user workflows end-to-end
- Check for console errors

**DON'T:**
- Only test with curl/API calls (backend testing alone is insufficient)
- Skip visual verification
- Mark tests passing without UI testing

## Step 7: Update feature_list.json (CAREFULLY!)

**YOU CAN ONLY MODIFY ONE FIELD: "passes"**

After thorough verification, change:
```json
"passes": false
```
to:
```json
"passes": true
```

**NEVER:**
- Remove features
- Edit feature descriptions
- Modify feature steps
- Combine or consolidate features
- Reorder features

**ONLY change "passes" field AFTER verification through the UI.**

## Step 8: Commit Your Progress

```bash
git add -A
git commit -m "feat: <description>

- Added <specific changes>
- Tested through UI at localhost:5173
- Updated feature_list.json: marked feature as passing"
```

## Step 9: Update Progress Notes

Append to `claude-progress.txt`:

```
### Session [N] - [Date]
**Progress:** X/Y features passing

**Completed:**
- Feature: <name> - <brief description>

**Issues Encountered:**
- <any blockers or problems>

**Next Session Should:**
- <specific next steps>
- <any warnings or gotchas>
```

## Step 10: Exit Session

After completing ONE feature:
1. Ensure all code is committed
2. Update claude-progress.txt
3. Leave the app in a working state
4. **Exit** - another session will continue

---

## Code Quality Guidelines

### AVOID:
- Unnecessary comments (code should be self-explanatory)
- Unnecessary defensive try/catch blocks
- Casting to `any` to bypass TypeScript (fix the types properly)
- Over-engineering for hypothetical future requirements
- Adding features beyond what was specified

### PREFER:
- Well-maintained libraries over custom implementations
- Simple, focused solutions
- Existing patterns in the codebase
- Self-documenting code with clear naming

### Use Established Libraries:
- `date-fns` or `dayjs` for dates (not moment.js)
- `zod` for validation
- `react-hook-form` for forms
- `@tanstack/react-query` for data fetching

---

## Rules Summary

1. **ONE feature per session** - Complete and commit before moving on
2. **Test through UI** - Not just API calls
3. **Fix regressions first** - Before new work
4. **Leave codebase working** - No broken features when you exit
5. **Document your work** - claude-progress.txt is the handoff
6. **If blocked** - Document clearly and move to next feature
