# Contributing

We welcome contributions of all kinds. See [CONTRIBUTING.md](https://github.com/ShrekDino/Project-FreeGen/blob/main/CONTRIBUTING.md) in the repository root for full instructions.

## Quick Links

- [GitHub Repository](https://github.com/ShrekDino/Project-FreeGen)
- [Issue Tracker](https://github.com/ShrekDino/Project-FreeGen/issues)
- [Discussions](https://github.com/ShrekDino/Project-FreeGen/discussions)

## Development Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/Project-FreeGen.git
cd Project-FreeGen
git remote add upstream https://github.com/ShrekDino/Project-FreeGen.git

# Create feature branch
git checkout -b feat/my-feature

# Make changes, then:
./scripts/manage.sh format   # Format code
./scripts/manage.sh lint     # Run linter
./scripts/manage.sh test     # Run tests
./scripts/manage.sh build release  # Build release

# Commit and push
git add .
git commit -m "feat: add my awesome feature"
git push -u origin feat/my-feature
```

## Adding Effects

See [Effects Documentation](effects.md) for detailed instructions on adding new upscalers, frame generators, or filters.
