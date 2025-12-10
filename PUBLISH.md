# Publishing

This project uses GitHub Actions for automated releases. **Do not manually run `npm version` or `npm publish`.**

## How to Release

1. Commit your changes to `main` with conventional commit messages:
   - `fix:` → patch release (0.0.x)
   - `feat:` → minor release (0.x.0)
   - `feat!:` or `BREAKING CHANGE` → major release (x.0.0)
   - `chore:`, `docs:`, etc. → patch release

2. Push to `main`:
   ```bash
   git push origin main
   ```

3. The GitHub Actions workflow will automatically:
   - Determine version bump from commit messages
   - Update `package.json` version
   - Create a git tag
   - Publish to npm with provenance
   - Create a GitHub Release

## Manual Trigger

For explicit version control, use the GitHub Actions UI:
1. Go to Actions → "Release and Publish"
2. Click "Run workflow"
3. Select version type (patch/minor/major)
