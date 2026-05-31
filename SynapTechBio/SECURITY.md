# SynapTechBio — Security Policy

> *The DCSL is built on trust. We take security seriously.*
> *Current reality: security architecture is designed but not fully deployed. No production infrastructure exists yet.*

---

## Reporting a Vulnerability

If you discover a security vulnerability in SynapTechBio's platform, infrastructure, or any related repository, please report it confidentially:

**Email**: SamiT2825@synaptechbio.org

Please do **not** report security vulnerabilities via public GitHub issues.

### What to Include

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if known)
- Your contact for follow-up

### Response Timeline

| Timeframe | Action |
|-----------|--------|
| 24 hours | Acknowledgment of receipt |
| 72 hours | Initial assessment and severity rating |
| 1 week | Fix in development or mitigation plan |
| Responsible disclosure | Coordinated public disclosure after fix |

---

## Security Architecture

SynapTechBio's security is built on the **Data Capture Split Layer (DCSL)**:

| Layer | Protection |
|-------|------------|
| **Encryption** | AES-256-GCM for all proprietary researcher data |
| **Anonymization** | PII stripped, SHA-256 hashed before storage |
| **Isolation** | Per-tenant S3 buckets and Pinecone namespaces |
| **Auth** | JWT + API key validation (optional but recommended) |
| **HTTPS** | All API endpoints served over TLS |

---

## Bug Bounty

We do not currently have a formal bug bounty program, but we will gratefully acknowledge security researchers who responsibly disclose vulnerabilities.

---

## Known Security Gaps

| Issue | Status | Target Fix |
|-------|--------|------------|
| Auth middleware defined but unwired | ⚠️ Unwired | P0 (Week 1-3) |
| No rate limiting on API endpoints | ⚠️ Missing | P3 (Week 10-13) |
| S3 upload is a no-op | ⚠️ No-op | P1 (Week 4-6) |
| No multi-tenancy isolation | ⚠️ Missing | P0 (Week 1-3) |
| Telemetry query API is unauthenticated | ⚠️ Missing auth | P3 (Week 10-13) |
