# Contributing

This monorepo uses `git subtree` to track upstream repositories. The original repos remain the primary development targets.

## Submitting Changes

1. Fork or work directly in the relevant package directory
2. Submit PRs to the **original repository** (see MONOREPO_MAP.md)
3. The monorepo is updated via subtree pulls

## Code Style

- Python: Follow PEP 8, use type hints
- TypeScript: Follow existing patterns in `packages/idre/src/frontend/`
- No comments unless explaining non-obvious design decisions
- Keep functions small and single-purpose

## Running Tests

```bash
# Test specific package
cd packages/csdf && pytest

# Test all packages
for pkg in packages/*/; do
  (cd "$pkg" && pytest 2>/dev/null && echo "$pkg OK")
done
```

## License

MIT — same as all sub-projects.
