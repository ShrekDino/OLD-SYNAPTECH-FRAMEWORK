# Changelog

## [0.1.0] — 2026-05-24

### Added
- **Argon2id Proof-of-Work**: Replaced Bitcoin's SHA-256d with Argon2id (memory-hard, ASIC-resistant PoW)
  - 256 MiB memory requirement
  - 3 passes, 2 lanes parallelism
  - Network-unique salt based on SHA256("DigiDollar PoW")
- **New genesis block**: Fresh blockchain starting point with Argon2id-mined genesis
- **libargon2 dependency**: Required for Argon2id PoW verification

### Changed
- Rebranded all binaries: `digidollard`, `digidollar-qt`, `digidollar-cli`, `digidollar-tx`, `digidollar-wallet`, `digidollar-util`
- Updated chain parameters for DigiDollar network
- All documentation updated for DigiDollar project

### Removed
- SHA-256d PoW algorithm (replaced by Argon2id)
- Bitcoin-specific branding and references throughout codebase

### Security
- ASIC-resistant mining ensures decentralized participation
- Memory-hard PoW prevents specialized hardware advantage

[0.1.0]: https://github.com/ShrekDino/digidollar/releases/tag/v0.1.0
