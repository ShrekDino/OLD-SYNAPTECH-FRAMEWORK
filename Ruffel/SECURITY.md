# Security Policy for Ruffel Mono Agent

> **Last updated:** 2026-05-25

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x (beta) | ✅ |

The project is in beta. Security patches will be applied to the latest release.

---

## Reporting a Vulnerability

**Do not file a public GitHub issue for security vulnerabilities.**

Instead, contact the maintainer directly via one of these methods:

1. **GitHub Security Advisory**: Navigate to the repository → "Security" tab → "Report a vulnerability"
2. **Direct message**: Contact `ShrekDino` on GitHub

You should receive an acknowledgment within 48 hours. We will:
- Confirm receipt within 2 business days
- Provide an initial assessment within 5 business days
- Release a fix based on severity:
  - **Critical**: within 7 days
  - **High**: within 14 days
  - **Medium**: within 30 days
  - **Low**: next release cycle

---

## Security Architecture

### Threat Model

Ruffel Mono Agent runs entirely locally and does not make network connections except to:
- The local LLM inference server (`localhost:7474`)
- MCP servers configured by the user
- Web fetch/search tools (user-initiated)

### Key Security Mechanisms

| Mechanism | Description |
|-----------|-------------|
| **Offline-first** | Zero cloud dependencies. All inference, processing, and storage is local. No telemetry. No API calls to external services. |
| **Secret scanning** | `SecretScanner.Redact()` screens all output for 30+ credential patterns (AWS keys, API tokens, SSH keys, JWT, connection strings) before crossing any process boundary. Applied at the JSON-RPC serialization layer — a single choke point. |
| **Permission system** | Every tool execution must pass through the permission engine. Tools declare their required permission level (AutoAllow/Ask/Deny) or capabilities. Dangerous operations (shell execution, file writes, network egress) always prompt the user. |
| **Path traversal protection** | `SanityCheck` validates all file paths to prevent directory traversal attacks. Only paths within the working directory are allowed (unless explicitly permitted). |
| **Blocked binaries** | `sudo`, `su`, `chmod`, `chown`, `attrib`, and other privilege-escalation or destructive commands are blocked by default. |
| **Plan mode** | When active, all write tools (FileWrite, Bash, etc.) are blocked. The agent can only read and investigate. |
| **Doom loop prevention** | Prevents the LLM from making repeated identical tool calls — stops infinite loops caused by misconfiguration or adversarial prompts. |
| **stdin/stdout isolation** | Communication uses line-delimited JSON-RPC on stdio. No network ports, HTTP, or gRPC — zero network attack surface. `Console.SetOut(Console.Error)` redirects all stray writes to stderr. |

---

## Known Security Considerations

### 1. Prompt Injection

The agent executes LLM-generated tool calls. While the permission system blocks dangerous operations, a malicious prompt could attempt to:
- Social-engineer the user into allowing dangerous operations
- Inject instructions via codebase files the agent reads

**Mitigations:**
- Permission prompts require explicit user consent for dangerous tools
- The system prompt includes instructions to reject harmful requests
- Users should review tool summaries before allowing

### 2. Secret Leakage via Tool Output

Tool output containing secrets could be returned to the LLM context and potentially appear in subsequent responses.

**Mitigations:**
- `SecretScanner.Redact()` screens all tool output before it reaches the LLM
- Redaction is applied at the JSON-RPC serialization layer — every byte leaving the process is scanned
- The VS Code extension and terminal client both display redacted content

### 3. File System Access

The agent has access to files within the working directory. Path traversal checks prevent reading/writing outside this boundary, but files within the directory are accessible.

**Mitigations:**
- `SanityCheck.ValidateFilePath()` rejects paths containing `..` or absolute paths outside the working directory
- File writes trigger permission prompts
- `FileHistory` enables atomic undo of all file modifications

### 4. MCP Server Connections

MCP servers are user-configured and run as subprocesses. They have access to the same file system as the agent.

**Mitigations:**
- MCP servers are not auto-discovered — user must configure them explicitly
- MCP tool execution goes through the same permission system
- Users should only connect trusted MCP servers

---

## Secret Patterns Detected

`SecretScanner.Redact()` detects and redacts the following patterns (non-exhaustive):

| Pattern | Example Hit |
|---------|-------------|
| AWS Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| AWS Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| GitHub Personal Access Token | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| GitHub App Token | `ghs_xxxxxxxxxxxxxxxxxxxx` |
| OpenAI API Key | `sk-xxxxxxxxxxxxxxxxxxxxxxxx` |
| Anthropic API Key | `sk-ant-xxxxxxxxxxxxxxxxxxxx` |
| Slack Bot Token | `xoxb-xxxxxxxxxxxxxxxx` |
| Slack Webhook URL | `https://hooks.slack.com/services/T000000/B000000/xxxxxxxx` |
| Discord Webhook URL | `https://discord.com/api/webhooks/000000/xxxxxxxx` |
| JWT Token | `eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.xxxxxxxx` |
| SSH Private Key | `-----BEGIN OPENSSH PRIVATE KEY-----` |
| Generic Bearer Token | `Authorization: Bearer xxxxxxxx` |
| MongoDB Connection String | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| PostgreSQL Connection String | `postgresql://user:pass@localhost:5432/db` |
| Google OAuth Token | `ya29.xxxxxxxxxxxxxxxxxxxx` |
| GitLab Token | `glpat-xxxxxxxxxxxxxxxxxxxx` |

---

## Security Checklist for Users

- [ ] Run the agent in a dedicated user account (not root)
- [ ] Use the Docker deployment for maximum isolation
- [ ] Review tool permission summaries before allowing
- [ ] Do not share session files (`~/.openmono/sessions/`)
- [ ] Keep the system updated (pull latest from `dev` branch)
- [ ] Use strong API keys if connecting to cloud LLMs
- [ ] Review MCP server configurations regularly

---

## Security Checklist for Contributors

- [ ] No secrets in code, comments, or documentation
- [ ] No `Console.WriteLine()` in library code (use the logging system)
- [ ] All file paths validated with `SanityCheck`
- [ ] Permission checks before dangerous operations
- [ ] SecretScanner.Redact() applied to any new output path
- [ ] Async all the way — no `.Result` or `.Wait()` (deadlock risk)
- [ ] Cancellation tokens forwarded to all async operations
