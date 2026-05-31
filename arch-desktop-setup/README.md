# Arch Linux Interactive Installer

> **Detect → Prompt → Build → Review → Execute** — Learning Arch should be this easy.

A hardware-aware Arch Linux installer with interactive prompts, multiple desktop environments,
LUKS encryption, and auto-detected drivers. Open source, community-first.

## Quick Start

From the Arch Linux live ISO (UEFI mode):

```bash
pacman -Sy git --noconfirm
git clone https://github.com/ShrekDino/arch-desktop-setup.git
cd arch-desktop-setup && bash install.sh
```

### Alternative (curl)

```bash
curl -sL https://raw.githubusercontent.com/ShrekDino/arch-desktop-setup/master/install.sh | bash
```

### Post-Install

After rebooting, optionally run the finish script to handle any remaining setup:

```bash
bash ~/arch-desktop-setup/finish_setup.sh
```

## Features

| Feature | Description |
|---------|-------------|
| Hardware detection | Auto-detects CPU microcode, GPU drivers, VM guest |
| Interactive prompts | Hostname, username, locale, timezone, keymap, LUKS |
| Desktop choice | GNOME 50, KDE Plasma, or CLI-only |
| Profiles | Full, Minimal, or Custom (pick per category) |
| Disk layout | GPT → (LUKS) → LVM → btrfs subvolumes |
| GPU drivers | NVIDIA (open-dkms), AMD (mesa + vulkan), Intel (mesa) |
| Audio | PipeWire + WirePlumber |
| Networking | NetworkManager, bluetooth, firewalld |
| AUR | yay + miniconda3, pamac-aur, signal-cli, tetrd, appimagelauncher |

## Customizing

- **`packages/`** — add/remove packages by category
- **`configs/`** — system configuration files
- **`dotfiles/`** — .bashrc, .bash_profile, .gitconfig
- **`install.sh`** — tweak prompts, defaults, or install logic
