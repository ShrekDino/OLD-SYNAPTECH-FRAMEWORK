# Contributing to DigiDollar

Thank you for your interest in contributing to DigiDollar! We welcome contributions from everyone. Whether you're fixing a bug, adding a feature, or improving documentation, your help is appreciated.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**: `git clone https://github.com/ShrekDino/digidollar.git`
3. **Create a topic branch**: `git checkout -b my-feature-branch`
4. **Make your changes** following the coding conventions
5. **Test your changes** — run `make check` and relevant test suites
6. **Commit** with a clear, descriptive message
7. **Push** to your fork and submit a pull request

## Pull Request Guidelines

- Keep changes focused and atomic. A PR should do one thing well.
- Write clear commit messages: a short subject line (50 chars max), a blank line, then detailed explanation.
- Prefix the PR title with the relevant area: `consensus:`, `wallet:`, `net:`, `rpc:`, `build:`, `doc:`, `test:`, `gui:`.
- Include tests for new features or bug fixes when possible.
- Update documentation if your change affects user-facing behavior.

## Coding Standards

DigiDollar follows the same coding standards as Bitcoin Core:

- **C++**: See [doc/developer-notes.md](doc/developer-notes.md)
- **Python**: Follow PEP 8 (enforced by `.style.yapf`)
- **Shell scripts**: Follow the existing patterns

## Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Pull Requests**: All code contributions go through PRs

## Security Issues

**Do not open public issues for security vulnerabilities.** Please see [SECURITY.md](SECURITY.md) for responsible disclosure.

## Code of Conduct

Be respectful and constructive. We are all here to build great software.

## License

By contributing to DigiDollar, you agree that your contributions will be licensed under the MIT License (see [COPYING](COPYING)).
