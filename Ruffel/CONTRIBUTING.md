# Contributing to Ruffel Mono Agent

> **Last updated:** 2026-05-25

We welcome contributions of all kinds — bug reports, feature requests, documentation improvements, and code changes. Please read this guide before contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
  - [C# (.NET 10)](#c-net-10)
  - [TypeScript](#typescript)
  - [Git Commit Messages](#git-commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Security](#security)

---

## Code of Conduct

This project follows a **zero-tolerance policy for harassment, discrimination, or toxic behavior**. We are committed to providing a welcoming and inclusive environment for everyone.

- Be respectful and constructive in all communications
- Accept constructive criticism gracefully
- Focus on what is best for the community and the project
- Show empathy towards other community members

Violations should be reported to the project maintainer.

---

## Getting Started

### Prerequisites

- .NET 10 SDK
- Node.js 20+ (for terminal client and VS Code extension)
- Git
- A code editor (VS Code, Rider, or any C#-aware editor)

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Ruffel.git
cd Ruffel
git remote add upstream https://github.com/ShrekDino/Ruffel.git
```

### Set Up Development Environment

```bash
# Build the backend
dotnet build src/OpenMono.Cli

# Build the terminal client
cd terminal
npm install
npm run compile
npm link
cd ../..

# Build the VS Code extension
cd opencode/sdks/vscode
npm install
npm run compile
cd ../..
```

### Verify Everything Works

```bash
# Run backend tests
dotnet test src/OpenMono.Tests

# Run terminal client type check
cd terminal && npx tsc --noEmit && cd ../..

# Run VS Code extension type check
cd opencode/sdks/vscode && npx tsc --noEmit && cd ../..
```

---

## Development Environment

### Recommended VS Code Extensions

- **C# Dev Kit** — C# language support
- **EditorConfig for VS Code** — EditorConfig support
- **GitLens** — Git history visualization
- **Prettier** — Code formatting for TypeScript
- **ESLint** — TypeScript linting

### Branch Strategy

- `dev` — Development branch (default, base for PRs)
- `main` — Release branch (stable, production-ready)
- `feat/*` — Feature branches
- `fix/*` — Bug fix branches
- `docs/*` — Documentation branches

```bash
# Create a feature branch
git checkout dev
git pull upstream dev
git checkout -b feat/my-feature
```

---

## Project Structure

```
Ruffel/
├── src/
│   └── OpenMono.Cli/          # .NET 10 backend
│       ├── Config/             # Configuration system
│       ├── Rendering/          # Renderer implementations
│       ├── Session/            # Session management
│       ├── Tools/              # Tool implementations
│       ├── Permissions/        # Permission engine
│       ├── History/            # File history & undo
│       ├── Llm/                # LLM client abstractions
│       ├── Mcp/                # MCP server integration
│       ├── Memory/             # Memory persistence
│       ├── Hooks/              # Hook system
│       ├── Playbooks/          # Playbook workflow engine
│       ├── Tui/                # TUI renderer
│       └── Utils/              # Utilities
├── opencode/
│   └── sdks/
│       ├── terminal/           # Terminal client (TypeScript)
│       └── vscode/             # VS Code extension (TypeScript)
├── docker/                     # Docker configuration
└── docs/                       # Documentation
```

Each module should have a clear single responsibility. If you find yourself creating cross-module dependencies, consider refactoring.

---

## Coding Standards

### C# (.NET 10)

We follow the [.NET coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions) with these additions:

```csharp
// ✅ Correct
public sealed class FileHistory : IDisposable
{
    private readonly string _baseDirectory;
    private readonly List<FileSnapshot> _snapshots = [];

    public IReadOnlyList<FileSnapshot> Snapshots => _snapshots;

    public async Task<List<string>> RevertAsync(int count, CancellationToken ct)
    {
        // Implementation
    }
}

// ❌ Avoid
class file_history  // PascalCase for classes
{
    private string baseDirectory;  // _prefix for private fields
    public List<FileSnapshot> snapshots = [];  // Use IReadOnlyList for public
}
```

**Rules:**

| Rule | Convention |
|------|-----------|
| File naming | PascalCase, matches type name |
| Visibility | Explicit `public`/`private`/`internal` — no implicit |
| Fields | `_camelCase` for private, `PascalCase` for public |
| Properties | `PascalCase` |
| Methods | `PascalCase` |
| Parameters | `camelCase` |
| Async | `Async` suffix on async methods |
| Nullable | Enable nullable reference types; use `?` suffix |
| `var` | Use `var` when type is obvious, explicit otherwise |
| Sealed | `sealed` on all non-abstract classes unless designed for inheritance |
| Records | `sealed record` for DTOs |
| Using directives | Inside namespace, alphabetical |
| Brace placement | Allman style (opening brace on new line) |

**Async patterns:**
- No `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` — always `await`
- Use `CancellationToken` as last parameter in async methods
- Fire-and-forget tasks use the `Forget()` extension method

### TypeScript

We follow the [TypeScript coding guidelines](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines) with these additions:

```typescript
// ✅ Correct
export class AgentController {
  private transport: JsonRpcTransport
  private running = false

  constructor(binaryPath: string, workDir: string) {
    this.transport = new JsonRpcTransport({ binaryPath, args: ["--rpc", "--dir", workDir] })
  }

  async start(): Promise<void> {
    await this.transport.start()
  }
}

// ❌ Avoid
class agent_controller {  // PascalCase for classes
  Transport: JsonRpcTransport  // camelCase for members
}
```

**Rules:**

| Rule | Convention |
|------|-----------|
| File naming | PascalCase, matches main export |
| Classes/Interfaces | PascalCase |
| Methods/Functions | camelCase |
| Properties/Fields | camelCase |
| Constants | UPPER_SNAKE_CASE or camelCase (context-dependent) |
| Async | `async`/`await` always (no raw promises) |
| Types | Prefer `interface` for public contracts, `type` for unions |
| Imports | `import` (ESM), no `require()` |
| Semicolons | Required |
| Strict mode | Always `"strict": true` in tsconfig |
| Null checks | Use `??` and `?.` operators |

### Git Commit Messages

We use **conventional commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code refactoring (no feature/bug change)
- `test` — Test additions/changes
- `chore` — Build, CI, dependencies
- `style` — Formatting (no logic change)
- `perf` — Performance improvement

**Scopes:**
- `core` — Backend C# code
- `terminal` — Terminal client (TypeScript)
- `vscode` — VS Code extension
- `config` — Configuration system
- `permissions` — Permission engine
- `tools` — Tool implementations
- `docs` — Documentation
- `docker` — Docker configuration

**Examples:**
```
feat(core): add input/cancel method for turn cancellation
fix(terminal): handle null delta in text/delta notification
docs(api): document new permission/ask notification format
refactor(core): extract JSON-RPC server base class
test(core): add ToolDispatcher permission integration tests
```

---

## Pull Request Process

### 1. Before You Start

- Search existing issues and PRs to avoid duplicates
- Discuss significant changes in an issue first
- For bugs, include reproduction steps

### 2. Development

```bash
# Create branch from dev
git checkout dev
git pull upstream dev
git checkout -b feat/my-feature

# Make changes, then verify
dotnet build src/OpenMono.Cli           # Backend compiles
npx tsc --noEmit                        # Terminal client typechecks
node esbuild.js                          # Terminal client builds
dotnet test src/OpenMono.Tests          # Tests pass
```

### 3. Commit

```bash
git add .
git commit -m "feat(core): add my new feature"
```

Keep commits focused: one logical change per commit. Use `git add -p` for partial staging.

### 4. Push and PR

```bash
git push origin feat/my-feature
```

Then open a PR on GitHub against `ShrekDino/Ruffel:dev`.

### 5. PR Requirements

- **Title**: Follow conventional commit format
- **Description**: Explain what and why, not how (the code shows how)
- **Tests**: Include tests for new functionality
- **Documentation**: Update relevant docs (ARCHITECTURE.md, docs/API.md, etc.)
- **Build**: Must pass CI (build + test + lint)
- **Review**: At least one maintainer review required

### 6. After Merge

```bash
git checkout dev
git pull upstream dev
git branch -d feat/my-feature
```

---

## Testing

### Backend Tests

```bash
# Run all tests
dotnet test src/OpenMono.Tests

# Run specific test class
dotnet test src/OpenMono.Tests --filter "FullyQualifiedName~ToolDispatcherTests"

# Run with verbose output
dotnet test src/OpenMono.Tests -v n
```

### Writing Tests

- Use xUnit
- Avoid mocks where possible — prefer integration tests with real components
- Test file name: `{ComponentName}Tests.cs`
- Test method name: `{MethodName}_{Scenario}_{ExpectedResult}`

```csharp
[Fact]
public async Task ExecuteSingleToolAsync_UnknownTool_ReturnsError()
{
    var dispatcher = CreateDispatcher();
    var call = new ToolCall { Id = "1", Name = "NonExistentTool", Arguments = "{}" };
    var tool = new FileReadTool();
    var context = CreateContext();

    var result = await dispatcher.ExecuteSingleToolAsync(call, tool, context, CancellationToken.None);

    Assert.True(result.IsError);
}
```

### Terminal Client Tests

```bash
cd terminal
# No test runner configured yet — run type check as minimum validation
npx tsc --noEmit
```

---

## Documentation

Documentation lives in two places:

| Location | Content |
|----------|---------|
| `root *.md` | README.md, ARCHITECTURE.md, SETUP.md, CONFIG.md, CONTRIBUTING.md, SECURITY.md |
| `docs/*.md` | API.md (protocol spec), DEVELOPMENT.md, COMPREHENSIVE_REFERENCE.md |

**Documentation standards:**
- Markdown with GitHub Flavored Markdown
- Code blocks should specify language
- Diagrams should use ASCII art (monospace-compatible)
- Keep line length under 100 characters
- Update documentation in the same PR as code changes

---

## Issue Reporting

### Bug Reports

Include:
1. **Environment**: OS, .NET version, Node.js version, Docker version
2. **Steps to reproduce**: Minimal, complete, verifiable
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens (include logs)
5. **Screenshots**: For UI issues

### Feature Requests

Include:
1. **Problem**: What problem does this solve?
2. **Solution**: Proposed implementation
3. **Alternatives**: Other approaches considered
4. **Context**: How does this fit into the project?

---

## Security

See [SECURITY.md](SECURITY.md) for our security policy. For vulnerability disclosures, please contact the maintainer directly — do not file a public issue.

---

## Getting Help

- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Maintainer**: Contact via GitHub

---

<div align="center">
  <sub>Thank you for contributing to Ruffel Mono Agent!</sub>
</div>
