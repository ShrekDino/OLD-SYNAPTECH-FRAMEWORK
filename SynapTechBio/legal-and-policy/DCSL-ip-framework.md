# SynapTechBio — DCSL IP Framework

> *Data Capture Split Layer: Technical and legal architecture for IP sovereignty in community-governed AI research.*

---

## 1. What is DCSL?

The **Data Capture Split Layer** is SynapTechBio's core cryptographic middleware that executes a real-time fork on every request entering the IDRE platform:

- **Proprietary Path**: Researcher's IP → AES-256-GCM encrypted → Immutable S3 bucket (researcher-controlled)
- **Public Path**: Anonymized telemetry → Pinecone vector DB → Continuous alignment → Living Blueprint

**The DCSL is both a technical moat and a legal framework.** It guarantees that:
1. SynapTechBio **cannot read** researcher IP (we don't have the keys)
2. The community **benefits** from aggregated, anonymized learnings
3. Traditional AI **cannot scrape** the proprietary dataset

---

## 2. Technical Architecture

```
Request → CaptureSplitMiddleware
              │
              ▼
    ┌────────────────────┐
    │  request.body()    │
    └────────┬───────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
Proprietary    Anonymized
   IP           Telemetry
      │             │
      ▼             ▼
AES-256-GCM    PII Strip +
 Encrypt      SHA-256 Hash
      │             │
      ▼             ▼
  S3 Bucket    Pinecone
(immutable)   Vector DB
```

### Encryption Details

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-256-GCM |
| Key Size | 32 bytes (256 bits) |
| Nonce Size | 12 bytes (random per encryption) |
| AAD | Empty (configurable to request path) |
| Key Management | Per-instance generation at startup (production: KMS-derived) |

### Telemetry Anonymization

| Field | Treatment |
|-------|-----------|
| `user_id` | SHA-256 hash with salt |
| `email` | Stripped entirely |
| `ip_address` | Stripped entirely |
| `auth_token` | Stripped entirely |
| `neuron_ids` | Forwarded (needed for topology hash) |
| `operation` | Forwarded (anonymized operation type) |
| `timestamp` | Forwarded (no PII in timestamps) |

---

## 3. Legal Framework

### Researcher Rights

1. **Right to IP Sovereignty**: All data you generate on the platform is yours. Encrypted before we see it. We cannot decrypt.
2. **Right to Telemetry Access**: You can query the anonymized telemetry commons for similarity search.
3. **Right to Audit**: The alignment pipeline is transparent. All model changes are logged and published.
4. **Right to Exit**: Export your encrypted data from S3 at any time. No data lock-in.

### SynapTechBio Obligations

1. **Never request encryption keys**: The per-instance key is generated at service startup and never persisted.
2. **Never decrypt user data**: The alignment pipeline works on telemetry only, not raw IP.
3. **Always publish model updates**: The Living Blueprint is updated transparently.
4. **Maintain open weights**: The foundation model is community-owned.

### Community Rights

1. **Access to the Living Blueprint**: Always free, always open weights.
2. **Governance participation**: Through RFC process and community council.
3. **Transparency**: All alignment operations are logged and queryable.

---

## 4. Moat Analysis

| Attack Vector | DCSL Defense |
|---------------|--------------|
| Competitor scrapes proprietary IP | AES-256-GCM encrypted before storage. No access without keys. |
| Competitor scrapes telemetry | Telemetry is anonymized + hashed. No PII, no raw IP. |
| Competitor copies the Living Blueprint | It's open weights. That's the point. But they can't copy the telemetry pipeline that generates it. |
| Malicious actor compromises S3 | Data is encrypted at rest. Per-instance key not stored with data. |
| Malicious actor compromises Pinecone | No PII, only anonymized operation fingerprints. |

---

## 5. Roadmap

| Feature | Status | Target |
|---------|--------|--------|
| AES-256-GCM encrypt/decrypt | ✅ Done | Implemented |
| PII stripping + hashing | ✅ Done | Implemented |
| Pinecone telemetry upsert | ✅ Wired | Active |
| S3 upload (per-tenant) | 📋 Planned | P1 (Week 4-6) |
| Per-tenant bucket isolation | 📋 Planned | P0 (Week 1-3) |
| KMS key management | 📋 Planned | P4 (Week 14-17) |
| Telemetry query UI | 📋 Planned | P2 (Week 7-9) |
| Public telemetry API | 📋 Planned | P3 (Week 10-13) |

---

## 6. Compliance & Regulatory

- **HIPAA/GDPR readiness**: DCSL architecture is designed for medical data compliance. PII is stripped before storage.
- **Export control**: Neural data classification under review. Consult legal counsel before onboarding international researchers.
- **Open science mandates**: Aligns with NIH/NSF data management requirements (FAIR principles).
