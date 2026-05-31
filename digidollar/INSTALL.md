# Installation

DigiDollar uses the GNU Autotools build system.

**Prerequisite**: [libargon2](https://github.com/P-H-C/phc-winner-argon2) must be installed.

See the platform-specific build guides in [doc/](doc/):
- [Unix](doc/build-unix.md)
- [macOS](doc/build-osx.md)
- [Windows](doc/build-windows.md)
- [Android](doc/build-android.md)

### Quick start

```bash
./autogen.sh
./configure
make -j$(nproc)
make install  # optional
```

The build produces the following binaries in `src/`:
- `digidollard` — headless daemon
- `digidollar-qt` — GUI client (if Qt enabled)
- `digidollar-cli` — command-line interface
- `digidollar-tx` — transaction tool
- `digidollar-wallet` — wallet tool
- `digidollar-util` — utility tool
