# Security Policy

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in FreeGen, please report it privately.

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please email the maintainer directly, or open a [security advisory](https://github.com/ShrekDino/Project-FreeGen/security/advisories/new).

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Scope

Security issues in the following areas are in scope:

- Buffer overflows in image processing
- Memory safety in the capture pipeline
- Unsafe deserialization in config files
- Privilege escalation via IPC

## Out of Scope

- Theoretical vulnerabilities without a demonstrated exploit path
- Issues requiring physical access to the machine
- Vulnerabilities in third-party dependencies (report upstream)
