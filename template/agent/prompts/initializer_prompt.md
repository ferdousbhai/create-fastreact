# Initializer Session

You are starting a NEW project. Your task is to analyze the app description and create a comprehensive feature list.

## Step 1: Read the App Specification
Read `app_spec.md` to understand what the user wants to build.

## Step 2: Create feature_list.json
Based on the app description, create `feature_list.json` with this EXACT structure:

```json
{
  "projectName": "<from app_spec>",
  "generatedAt": "<ISO timestamp>",
  "categories": [
    {
      "name": "Category Name",
      "features": [
        {
          "id": "unique-feature-id",
          "name": "Feature Name",
          "description": "What this feature does",
          "testSteps": ["Step 1", "Step 2", "Step 3"],
          "passes": false
        }
      ]
    }
  ]
}
```

## Guidelines for Feature Breakdown
1. Break the app into logical categories (e.g., "API", "Authentication", "Core Features", "UI")
2. Each feature should be small enough to implement in one session (~30 min of work)
3. Include specific, verifiable test steps for each feature
4. Order features by dependency (foundational features first)
5. Start with API/backend setup, then frontend
6. Include 15-30 features total depending on app complexity
7. All features start with `"passes": false`

## Step 3: Set Up Project Structure
Create any necessary directories or placeholder files for the planned architecture.

## Step 4: Initial Commit
```bash
git add -A
git commit -m "Initialize project with feature_list.json"
```

## Step 5: Update Progress
Append to `claude-progress.txt`:
- Summary of planned features
- Recommended implementation order
- Any assumptions made about the requirements

**IMPORTANT**: Do NOT implement any features yet. Just create the plan in feature_list.json.
