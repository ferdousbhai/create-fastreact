# Coding Session

You are continuing work on a FastReact application. This is a FRESH context window - you have no memory of previous sessions.

## Step 1: Orient Yourself (MANDATORY)

```bash
pwd && ls -la
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'
cat claude-progress.txt
git log --oneline -10
cat app_spec.md
```

## Step 2: Start Servers (If Not Running)

```bash
cd backend && modal serve modal_app.py  # Note the Modal URL from output
cd frontend && pnpm run dev
```

Ensure `frontend/.env.local` has `VITE_API_URL`, `VITE_MODAL_KEY`, and `VITE_MODAL_SECRET`. If Modal URL changed, update it. If you see 401 errors, verify credentials match https://modal.com/settings/proxy-auth-tokens

## Step 3: Verification Test (CRITICAL!)

If there are passing features, verify 1-2 core ones still work at http://localhost:5173. Test UI flows and check console for errors.

**If you find ANY issues** (functional or visual): mark as `"passes": false` and fix BEFORE new work.

Skip if first session (no passing features).

## Step 4: Select Next Feature

Find the first feature where `"passes": false` in feature_list.json.
Focus on completing this ONE feature this session.

## Step 5: Implement the Feature

Write code in:
- `frontend/` - React 19 + TypeScript + Tailwind v4 + shadcn/ui
- `backend/` - FastAPI on Modal

Add UI components: `cd frontend && pnpm dlx shadcn@latest add <component-name>`

Common: `button`, `card`, `input`, `dialog`, `toast`, `form`

## Step 6: Verify with Browser Testing

**CRITICAL:** Test through actual UI - not just curl/API calls. Check all states (loading, error, success), complete user flows, and console errors.

## Step 7: Update feature_list.json

After UI verification, change `"passes": false` to `"passes": true`.

**NEVER** modify anything else (descriptions, steps, order) - only the `"passes"` field.

## Step 8: Commit and Document

```bash
git add -A && git commit -m "feat: <description>"
```

Update `claude-progress.txt` with: session number, features passing (X/Y), what you completed, issues encountered, and next steps.

## Step 9: Exit Session

After ONE feature: commit, update progress notes, leave app working, exit.

---

## Code Quality Guidelines

**Avoid:** unnecessary comments, defensive try/catch, casting to `any`, over-engineering, scope creep.

**Prefer:** established libraries, simple solutions, existing patterns, self-documenting code.

**Libraries:** `date-fns`/`dayjs` (dates), `zod` (validation), `react-hook-form` (forms), `@tanstack/react-query` (data fetching - already configured)

### Data Fetching Pattern:
Use Tanstack Query with the `api()` helper from `src/lib/api.ts`:

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

// GET request
const { data, isLoading, error } = useQuery({
  queryKey: ['items'],
  queryFn: () => api<Item[]>('/api/items')
})

// POST/PUT/DELETE
const queryClient = useQueryClient()
const mutation = useMutation({
  mutationFn: (newItem: CreateItem) => api<Item>('/api/items', {
    method: 'POST',
    body: JSON.stringify(newItem)
  }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] })
})
```

### Backend Caching:
Use `modal.Dict` for caching expensive computations or third-party API calls:

```python
cache = modal.Dict.from_name("my-cache", create_if_missing=True)

if key in cache:
    return cache[key]
result = expensive_call()
cache[key] = result
```

---

## Rules Summary

1. **ONE feature per session** - Complete and commit before moving on
2. **Test through UI** - Not just API calls
3. **Fix regressions first** - Before new work
4. **Leave codebase working** - No broken features when you exit
5. **Document your work** - claude-progress.txt is the handoff
6. **If blocked** - Document clearly and move to next feature

---

## ⚠️ SECURITY: Modal-Only Backend

**NEVER run backend code locally.** Always use `modal serve` or `modal deploy`.
