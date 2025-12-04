# Releasing

## Automatic Release

Push to `main` → automatic patch release (0.1.6 → 0.1.7)

## Manual Release

```bash
# Patch (bug fixes)
gh workflow run publish.yml

# Minor (new features)
gh workflow run publish.yml -f version=minor

# Major (breaking changes)
gh workflow run publish.yml -f version=major
```

Check status:

```bash
gh run watch
```

## Setup

Link GitHub repo as trusted publisher on [npmjs.com/package/create-fastreact/access](https://www.npmjs.com/package/create-fastreact/access):

- Owner: `<your-github-username>`
- Repository: `create-fastreact`
- Workflow: `publish.yml`
