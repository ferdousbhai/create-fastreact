# Coding Session

Continue implementing the application from feature_list.json.

## Step 1: Orient Yourself
1. Read `feature_list.json` to see all features and progress
2. Read `app_spec.md` for the full app description
3. Read `claude-progress.txt` for notes from previous sessions
4. Run `git log --oneline -5` to see recent commits

## Step 2: Select Next Feature
Find the first feature where `"passes": false`. This is your focus for this session.

## Step 3: Implement the Feature
- Write code in `frontend/` (React) and/or `backend/` (FastAPI)
- Use existing patterns in the codebase
- Add shadcn/ui components: `cd frontend && pnpm dlx shadcn@latest add <name>`
- Keep changes focused on the single feature

## Step 4: Test the Feature
- Start dev servers if needed:
  - Frontend: `cd frontend && pnpm run dev`
  - Backend: `cd backend && modal serve modal_app.py`
- Manually verify the feature works per its testSteps
- Check browser console for errors

## Step 5: Mark Complete
Update `feature_list.json`:
- Set `"passes": true` for the completed feature
- NEVER remove features or edit their descriptions

## Step 6: Commit
```bash
git add -A
git commit -m "feat: <description>"
```

## Step 7: Update Progress
Append to `claude-progress.txt`:
- What you implemented
- Any issues encountered
- Notes for next session

## Rules
- ONE feature per session
- Test before marking complete
- Commit after each feature
- Leave codebase in working state
- If blocked, document the issue and move to next feature
