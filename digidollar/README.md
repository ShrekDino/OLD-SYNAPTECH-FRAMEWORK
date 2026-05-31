# DigiDollar

**ASIC-resistant digital currency — putting mining power back in the hands of consumers.**

DigiDollar is a fork of Bitcoin Core v25.0 that replaces SHA-256d proof-of-work with **Argon2id**, a memory-hard function designed to resist ASIC/FPGA dominance. This allows anyone with a standard consumer CPU or GPU to participate in mining on a level playing field.

## Key Features

- **Argon2id Proof-of-Work** — Memory-hard (256 MiB), ASIC-resistant, GPU-friendly
- **Full Bitcoin Core compatibility** — Inherits Bitcoin's mature codebase: full node validation, wallet, GUI, RPC, and P2P network
- **Privacy & Security** — Inherits all Bitcoin Core security features (Tor, I2P, BIP39/BIP32 wallets, PSBT)
- **Consumer Mining** — Mine with commodity hardware; no specialized ASICs required

## Build & Installation

### Dependencies

In addition to the standard Bitcoin Core build dependencies, DigiDollar requires **libargon2**:

```bash
# Debian/Ubuntu
sudo apt-get install libargon2-dev

# macOS (Homebrew)
brew install argon2

# From source
git clone https://github.com/P-H-C/phc-winner-argon2.git
cd phc-winner-argon2 && make && sudo make install
```

### Build

```bash
./autogen.sh
./configure
make -j$(nproc)
```

Detailed build instructions for each platform are in [doc/](doc/):
- [Unix](doc/build-unix.md)
- [macOS](doc/build-osx.md)
- [Windows](doc/build-windows.md)
- [Android](doc/build-android.md)

### Run

```bash
# Headless daemon
./src/digidollard

# GUI (if Qt was enabled)
./src/qt/digidollar-qt

# Command-line interface
./src/digidollar-cli
```

## Mining

DigiDollar uses **Argon2id** with the following parameters:

| Parameter | Value |
|-----------|-------|
| Algorithm | Argon2id |
| Memory    | 256 MiB |
| Passes    | 3 |
| Parallelism | 2 lanes |
| Network salt | SHA256("DigiDollar PoW")[0:8] |

Miners can use any Argon2id-compatible software (e.g., `src/digidollard` built-in mining) or develop custom mining tools using the open-source specification.

## Project Status

DigiDollar is currently at **v0.1.0** (pre-release). The software is functional but should be considered experimental. Use at your own risk.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

See [SECURITY.md](SECURITY.md) for our vulnerability disclosure policy.

## License

DigiDollar is released under the terms of the MIT license. See [COPYING](COPYING) for more information.

## Acknowledgements

DigiDollar builds upon the incredible work of the [Bitcoin Core](https://bitcoincore.org/) developers. We thank them for their years of dedication to building a robust, secure, and decentralized digital currency.
