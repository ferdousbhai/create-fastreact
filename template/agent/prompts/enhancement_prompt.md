# Enhancement Session

You are adding NEW features to an EXISTING FastReact project. The project already has a `feature_list.json` with completed features.

## Step 1: Understand the Current State

```bash
# 1. Your working directory
pwd
ls -la

# 2. Check current progress
cat feature_list.json | grep -c '"passes": true'
cat feature_list.json | grep -c '"passes": false'

# 3. Read the existing feature list
cat feature_list.json

# 4. Read previous session notes
cat claude-progress.txt

# 5. See project history
git log --oneline -20
```

## Step 2: Read the New Requirements

Read `app_spec.md` for the new features being requested.

The file may have been updated with a new section like:
```
## New Features
- Feature A
- Feature B
```

Or it may be a completely new specification to add to the existing app.

## Step 3: Verify Modal Authentication

```bash
modal token show
```

If not authenticated, run `modal token new`.

## Step 4: Append New Features to feature_list.json

**CRITICAL: You must PRESERVE all existing features!**

Read the current `feature_list.json` and APPEND new features to the end.

**NEVER:**
- Remove existing features
- Modify existing feature descriptions
- Change the order of existing features
- Reset any `"passes": true` to false

**Format for new features:**
```json
{
  "category": "backend-api",
  "description": "New feature description",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "passes": false
}
```

### Standard Categories
- `backend-api` - FastAPI endpoints on Modal
- `frontend-ui` - React components and pages
- `state` - State management and data flow
- `auth` - Authentication and authorization
- `styling` - Tailwind/shadcn styling
- `integration` - Frontend-backend integration

## Step 5: Update app_spec.md

If the new requirements aren't already in `app_spec.md`, append them:

```markdown
---

## Enhancement: [Date]

### New Features Added
- Feature A: description
- Feature B: description

### Implementation Notes
- Any dependencies on existing features
- Architectural considerations
```

## Step 6: Update Progress Notes

Append to `claude-progress.txt`:

```
### Enhancement Session - [Date]

**Existing Features:** X passing

**New Features Added:**
1. [Feature name] - [brief description]
2. [Feature name] - [brief description]

**Implementation Order:**
1. Start with [feature] because [reason]
2. Then [feature]

**Notes:**
- Any dependencies or considerations
```

## Step 7: Commit Enhancement Setup

```bash
git add -A
git commit -m "feat: add new features to feature_list.json

- Added X new features for [enhancement description]
- Preserved all Y existing features
- Updated app_spec.md with new requirements"
```

---

**IMPORTANT**: Do NOT implement any features yet. Just update the feature list and documentation. The next coding session will implement the new features.
