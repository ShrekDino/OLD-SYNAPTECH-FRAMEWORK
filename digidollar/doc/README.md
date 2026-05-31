DigiDollar
=============

Setup
---------------------
DigiDollar is a digital currency node client based on Bitcoin Core v25.0, featuring ASIC-resistant Argon2id proof-of-work. It downloads and, by default, stores the entire history of transactions, which requires significant disk space. Depending on the speed of your computer and network connection, the synchronization process can take anywhere from a few hours to a day or more.

Running
---------------------
The following are some helpful notes on how to run DigiDollar on your native platform.

### Unix

Unpack the files into a directory and run:

- `src/digidollar-qt` (GUI) or
- `src/digidollard` (headless)

### Windows

Unpack the files into a directory, and then run `digidollar-qt.exe`.

### macOS

Drag DigiDollar to your applications folder, and then run DigiDollar.

### Need Help?

* Ask for help on the [GitHub Discussions](https://github.com/ShrekDino/digidollar/discussions) page.
* Open an issue on the [issue tracker](https://github.com/ShrekDino/digidollar/issues).

Building
---------------------
The following are developer notes on how to build DigiDollar on your native platform. They are not complete guides, but include notes on the necessary libraries, compile flags, etc.

- [Dependencies](dependencies.md)
- [macOS Build Notes](build-osx.md)
- [Unix Build Notes](build-unix.md)
- [Windows Build Notes](build-windows.md)
- [FreeBSD Build Notes](build-freebsd.md)
- [OpenBSD Build Notes](build-openbsd.md)
- [NetBSD Build Notes](build-netbsd.md)
- [Android Build Notes](build-android.md)

Development
---------------------
The repo's [root README](/README.md) contains relevant information on the development process and automated testing.

- [Developer Notes](developer-notes.md)
- [Productivity Notes](productivity.md)
- [Release Process](release-process.md)
- [Translation Process](translation_process.md)
- [Translation Strings Policy](translation_strings_policy.md)
- [JSON-RPC Interface](JSON-RPC-interface.md)
- [Unauthenticated REST Interface](REST-interface.md)
- [Shared Libraries](shared-libraries.md)
- [BIPS](bips.md)
- [Dnsseed Policy](dnsseed-policy.md)
- [Benchmarking](benchmarking.md)
- [Internal Design Docs](design/)

### Resources
* Discuss on the [GitHub Discussions](https://github.com/ShrekDino/digidollar/discussions) page.
* Open issues on the [issue tracker](https://github.com/ShrekDino/digidollar/issues).

### Miscellaneous
- [Assets Attribution](assets-attribution.md)
- [DigiDollar Configuration File](bitcoin-conf.md)
- [CJDNS Support](cjdns.md)
- [Files](files.md)
- [Fuzz-testing](fuzzing.md)
- [I2P Support](i2p.md)
- [Init Scripts (systemd/upstart/openrc)](init.md)
- [Managing Wallets](managing-wallets.md)
- [Multisig Tutorial](multisig-tutorial.md)
- [P2P bad ports definition and list](p2p-bad-ports.md)
- [PSBT support](psbt.md)
- [Reduce Memory](reduce-memory.md)
- [Reduce Traffic](reduce-traffic.md)
- [Tor Support](tor.md)
- [Transaction Relay Policy](policy/README.md)
- [ZMQ](zmq.md)

License
---------------------
Distributed under the [MIT software license](/COPYING).
