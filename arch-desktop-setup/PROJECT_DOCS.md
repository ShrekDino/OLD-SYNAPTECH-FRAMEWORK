# Arch Desktop Setup — Shweemier Installer

## Project Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Source Machine: Laptop (Shweem)](#2-source-machine-laptop-shweem)
3. [Target Machine: Desktop (Shweemier)](#3-target-machine-desktop-shweemier)
4. [Laptop → Desktop Migration Delta](#4-laptop--desktop-migration-delta)
5. [Repository Structure](#5-repository-structure)
6. [Install Script Walkthrough](#6-install-script-walkthrough)
7. [Package Lists](#7-package-lists)
8. [Configuration Files](#8-configuration-files)
9. [Dotfiles](#9-dotfiles)
10. [Usage Instructions](#10-usage-instructions)
11. [Customization Guide](#11-customization-guide)
12. [Key Design Decisions](#12-key-design-decisions)

---

## 1. Project Overview

### Purpose

Create a fully automated Arch Linux installer that replicates the configuration of an existing laptop ("Shweem") onto a new desktop machine ("Shweemier"). The installer is designed to be run from the Arch Linux live ISO and produces a complete, ready-to-use system with zero manual configuration after the initial prompts.

### Design Philosophy

- **Idempotent by structure**: Each step cleanly sets up its portion of the system.
- **Fail-fast**: `set -euo pipefail` ensures any error stops the install immediately.
- **Hardware-aware**: CPU vendor, GPU vendor, RAM, and VM status are auto-detected. The correct microcode, GPU drivers, and guest tools are selected without user input.
- **Interactive-first**: The script prompts for everything up front (hostname, username, locale, timezone, keymap, LUKS, desktop, profile) before touching the disk.
- **Three profiles**: Full (everything), Minimal (base + drivers + desktop only), Custom (browse each extra category and choose).
- **Review-before-destroy**: The script presents a full plan summary and requires explicit confirmation before touching the disk.
- **Modular**: Package lists are split into category files so the user can add/remove sections without editing the script.
- **Desktop choice**: GNOME (primary, 57 packages), KDE Plasma (curated, 15 packages), or CLI-only.

### Machines

| Property | Laptop (source) | Desktop (target) |
|----------|-----------------|------------------|
| Hostname | Shweem | Shweemier |
| CPU | AMD Ryzen 7 5800HS | AMD Ryzen 7 5800X |
| GPU | NVIDIA RTX 3060 (laptop) | NVIDIA RTX 2080 Super |
| RAM | 40 GB | 48 GB DDR4 |
| WiFi/BT | MediaTek MT7921 | Intel AX210 |
| Storage | 1 TB NVMe | TBD |
| Form factor | ASUS ROG G14 laptop | Custom desktop |
| Microcode | amd-ucode | amd-ucode |

---

## 2. Source Machine: Laptop (Shweem)

### 2.1 Hardware

- **Model**: ASUS ROG Zephyrus G14 (2022)
- **CPU**: AMD Ryzen 7 5800HS (8C/16T, Zen 3)
- **GPU**: NVIDIA GeForce RTX 3060 Laptop GPU (6 GB)
- **RAM**: 40 GB DDR4 (8 GB soldered + 32 GB SODIMM)
- **Storage**: Samsung NVMe 1 TB
- **WiFi/BT**: MediaTek MT7921 (mt7921e driver)
- **Audio**: Realtek ALC294 (AMD Audio CoProcessor)

### 2.2 Operating System

```
OS:        Arch Linux (rolling)
Kernel:    7.0.8-zen1-1-zen (linux-zen)
           + linux-lts 6.18.31 (fallback kernel)
Shell:     bash 5.x
Init:      systemd
```

### 2.3 Disk Layout

```
nvme0n1
├── nvme0n1p1  vfat    FAT32    /boot           (631 MB free / 38% used)
└── nvme0n1p2  LVM2_member
    └── ArchinstallVg-root  btrfs  →  @      →  /
                                     @home  →  /home
                                     @pkg   →  /var/cache/pacman/pkg
                                     @log   →  /var/log
```

- **Boot mode**: UEFI (no CSM)
- **Partition table**: GPT
- **LVM**: Volume group `ArchinstallVg`, single logical volume `root` (100% of VG)
- **Filesystem**: btrfs with `compress=zstd:3,ssd,discard=async,space_cache=v2`
- **Swap**: zram (zstd-compressed, managed by zram-generator)
- **No LUKS encryption**

### 2.4 fstab

```fstab
# /dev/mapper/ArchinstallVg-root  @    →  /     btrfs  compress=zstd:3,ssd,discard=async,subvol=/@
# /dev/mapper/ArchinstallVg-root  @home →  /home btrfs  compress=zstd:3,ssd,discard=async,subvol=/@home
# /dev/mapper/ArchinstallVg-root  @pkg  →  /var/cache/pacman/pkg  btrfs  compress=zstd:3,ssd,discard=async,subvol=/@pkg
# /dev/mapper/ArchinstallVg-root  @log  →  /var/log              btrfs  compress=zstd:3,ssd,discard=async,subvol=/@log
# nvme0n1p1  →  /boot  vfat  defaults
```

### 2.5 Kernel Command Line (GRUB)

```
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"
```

### 2.6 mkinitcpio

**Hook order** (from `/etc/mkinitcpio.conf`):
```
HOOKS=(base udev autodetect microcode modconf kms keyboard keymap consolefont lvm2 block filesystems fsck)
```

**Compression**: zstd

Key notes:
- `autodetect` reduces initramfs size by detecting only needed modules
- `microcode` loads AMD CPU microcode early
- `kms` enables kernel mode setting for early framebuffer
- `lvm2` activates LVM volumes before root mount
- `keyboard`, `keymap`, `consolefont` enable typing LUKS password (kept for compatibility even though no LUKS)

### 2.7 Bootloader

- **GRUB** version 2.14
- UEFI boot to `\EFI\Arch\grubx64.efi`
- `grub-btrfs` installed for snapshot-aware boot menu
- `GRUB_DISABLE_RECOVERY=true` to suppress recovery entries

### 2.8 Users & Groups

| User | UID | Groups | Shell |
|------|-----|--------|-------|
| root | 0 | root | /bin/bash |
| cinni | 1000 | wheel | /bin/bash |

Sudo: `%wheel ALL=(ALL:ALL) ALL` (uncommented).

### 2.9 System Configuration

| Setting | Value |
|---------|-------|
| Hostname | Shweem |
| Locale | en_US.UTF-8 |
| Timezone | America/Chicago |
| Keymap | us |
| X11 layout | us |
| X11 model | pc105+inet |
| X11 options | terminate:ctrl_alt_bksp |
| Console font | default8x16 |

### 2.10 Networking

- **Manager**: NetworkManager 1.56.1
- **WiFi**: wpa_supplicant (for WPA2/WPA3 enterprise connections)
- **Firewall**: firewalld 2.4.1 (default zone: public)
- **NM config**: `/etc/NetworkManager/conf.d/` — `tun*` interfaces marked unmanaged (for VPN/Tetrd tunnels)

### 2.11 Audio Stack

- **Session**: PipeWire 1.6.5 + WirePlumber 0.5.14
- **Protocols**: pipewire-pulse (PulseAudio replacement), pipewire-jack (JACK replacement)
- **ALSA**: pipewire-alsa
- **Codecs**: gst-plugin-pipewire
- **Firmware**: sof-firmware (Sound Open Firmware for AMD Audio CoProcessor)

### 2.12 Bluetooth

- **Stack**: bluez 5.86 + bluez-utils
- **Profiles**: A2DP, HFP, HSP, GATT
- **Service**: bluetooth.service (enabled at boot)

### 2.13 Printing

- **Scheduler**: cups 2.4.19
- **Policy kit**: cups-pk-helper (allows non-root admin)
- **GUI**: system-config-printer
- **Service**: cups.service, cups.socket (socket-activated)

### 2.14 Display

- **Display manager**: GDM 50.0 (GNOME Display Manager)
- **Desktop environment**: GNOME 50 (full session: gnome-shell 50.1)
- **Extensions**: dash-to-panel (73), appindicator (64)
- **GNOME apps**: full suite — nautilus, epiphany, gnome-console, gnome-text-editor, loupe (image viewer), papers (document viewer), decibels (audio), showtime (video), snapshot (camera), baobab (disk usage), gnome-system-monitor, gnome-calculator, gnome-calendar, gnome-contacts, gnome-maps, gnome-weather, gnome-clocks, gnome-characters, gnome-font-viewer, gnome-logs, gnome-connections, gnome-remote-desktop, gnome-color-manager, gnome-software (package manager), gnome-tweaks, etc.

### 2.15 GPU / NVIDIA

- **Driver**: nvidia-open-dkms 595.71.05 (open kernel module, Turing+ GPUs)
- **VA-API**: libva-nvidia-driver (NVIDIA VDPAU → VA-API bridge for hardware video acceleration)
- **Container**: nvidia-container-toolkit (allows Docker to use GPU)
- **Modules loaded**: nvidia, nvidia_modeset, nvidia_drm, nvidia_uvm
- **Modprobe config** (`/etc/modprobe.d/nvidia.conf`):
  - `NVreg_UseKernelSuspendNotifiers=1` (faster suspend/resume)
  - `NVreg_TemporaryFilePath=/var/tmp` (avoids tmpfs for NVIDIA temporary files)
  - `blacklist nouveau` (prevent open-source driver load)
- **Docker runtime**: nvidia (configured in `/etc/docker/daemon.json`)

### 2.16 Power Management

- **Laptop-specific**: asusd (ASUS ROG control), supergfxd (GPU switching), rog-control-center (GUI), power-profiles-daemon
- **ZRAM**: zram-generator with `[zram0] compression-algorithm=zstd` (replaces swap partition)
- **Snapper**: configured for `/` and `/home` with GRUB-btrfs integration for bootable snapshots

### 2.17 Storage / Snapshots

- Snapper tracks `/` (root) and `/home` for automatic time-based snapshots
- `grub-btrfsd.service` regenerates GRUB config when new snapshots appear, making them bootable entries

### 2.18 Docker

- **Runtime**: docker 29.5.0, docker-desktop 4.72.0 (AUR)
- **NVIDIA**: nvidia-container-runtime for GPU-accelerated containers
- **Config**: daemon.json defines `nvidia` runtime
- **Service**: docker.service (enabled)

### 2.19 Package Inventory

#### Explicitly Installed Packages (pacman -Qe)

**Core system:**
```
base 3-3
base-devel 1-2
linux-zen 7.0.8.zen1-1
linux-zen-headers 7.0.8.zen1-1
linux-lts 6.18.31-1
linux-lts-headers 6.18.31-1
linux-firmware 20260410-1
amd-ucode 20260410-1
btrfs-progs 7.0-1
lvm2 2.03.40-1
dkms 3.4.1-1
grub 2:2.14-1
efibootmgr 18-4
grub-btrfs 4.14-1
sudo 1.9.17.p2-2
```

**Development:**
```
cmake 4.3.2-1
git 2.54.0-1
github-cli 2.92.0-1
nvm 0.40.4-1
python-pipx 1.12.0-1
ripgrep 15.1.0-2
inotify-tools 4.25.9.0-1
smartmontools 7.5-1
```

**NVIDIA:**
```
nvidia-open-dkms 595.71.05-2
libva-nvidia-driver 0.0.17-1
nvidia-container-toolkit 1.19.0-1
```

**GNOME Desktop:**
```
gdm 50.0-2
gnome-shell 1:50.1-2
gnome-session 50.0-1
gnome-settings-daemon 50.1-1
gnome-control-center 50.1-1
gnome-software 50.1-1
gnome-backgrounds 50.0-1
gnome-calculator 50.0-1
gnome-calendar 50.0-2
gnome-characters 50.0-1
gnome-clocks 50.0-2
gnome-color-manager 3.36.2-1
gnome-connections 50.0-1
gnome-console 50.0-1
gnome-contacts 50.0-1
gnome-disk-utility 46.1-2
gnome-font-viewer 50.0-1
gnome-keyring 1:50.0-1
gnome-logs 50.0-1
gnome-maps 50.1-1
gnome-menus 3.38.1-1
gnome-music 1:49.1-2
gnome-remote-desktop 50.1-1
gnome-system-monitor 50.0-1
gnome-text-editor 50.1-1
gnome-tour 50.0-1
gnome-tweaks 49.0-2
gnome-user-docs 50.0-1
gnome-user-share 48.2-1
gnome-weather 50.0-1
baobab 50.0-1
decibels 49.6.1-1
epiphany 50.4-2
loupe 50.0-1
nautilus 50.1-1
orca 50.1.2-1
papers 50.1-1
rygel 1:45.1-1
showtime 50.0-1
simple-scan 50.0-1
snapshot 50.0-1
sushi 50.0-1
tecla 50.0-1
yelp 49.1-1
gnome-shell-extension-appindicator 1:64-1
gnome-shell-extension-dash-to-panel 73-1
xdg-desktop-portal-gnome 50.0-1
xdg-user-dirs-gtk 0.16-1
```

**GNOME data/interop:**
```
gvfs 1.60.0-2
gvfs-afc 1.60.0-2
gvfs-dnssd 1.60.0-2
gvfs-goa 1.60.0-2
gvfs-gphoto2 1.60.0-2
gvfs-mtp 1.60.0-2
gvfs-nfs 1.60.0-2
gvfs-onedrive 1.60.0-2
gvfs-smb 1.60.0-2
gvfs-wsdd 1.60.0-2
grilo-plugins 1:0.3.18-3
gst-thumbnailers 1.0.0-1
malcontent 0.14.0-4
```

**Audio:**
```
pipewire 1:1.6.5-1
pipewire-alsa 1:1.6.5-1
pipewire-jack 1:1.6.5-1
pipewire-pulse 1:1.6.5-1
wireplumber 0.5.14-1
gst-plugin-pipewire 1:1.6.5-1
libpulse 17.0+r98+gb096704c0-1
sof-firmware 2025.12.2-1
```

**Network:**
```
networkmanager 1.56.1-1
network-manager-applet 1.36.0-2
wpa_supplicant 2:2.11-5
bluez 5.86-6
bluez-utils 5.86-6
firewalld 2.4.1-1
```

**Printing:**
```
cups 2:2.4.19-1
cups-pk-helper 0.2.7-2
system-config-printer 1.5.18-6
```

**Containers & VMs:**
```
docker 1:29.5.0-1
```

**Utilities:**
```
btop 1.4.7-1
fastfetch 2.63.1-1
htop 3.5.1-1
nano 9.0-1
vim 9.2.0450-1
bash-completion 2.17.0-3
wget 1.25.0-4
fuse2 2.9.9-5
snapper 0.13.1-2
zram-generator 1.2.1-1
cliphist 1:0.7.0-2
wl-clipboard 1:2.3.0-1
wl-clip-persist 0.5.0-2
xdg-utils 1.2.1-2
```

**AI/ML:**
```
ollama 0.24.0-1
```

**Gaming:**
```
prismlauncher 11.0.2-1
```

**Laptop-specific (ASUS ROG):**
```
asusctl 6.3.7.r0.gde4297a1-2
rog-control-center 6.3.7.r0.gde4297a1-2
supergfxctl 5.2.7-2
power-profiles-daemon 0.30-1
```

**Other:**
```
appimagelauncher 3.0.0_beta_3-1      (AUR)
capella-bin 7.0.0.202407091438-2     (AUR, music notation)
docker-desktop 4.72.0-1              (AUR)
pamac-aur 11.7.4-3                   (AUR)
signal-cli 0.14.4.1-1                (AUR)
tetrd 1.3.1-1                        (AUR, tunnel service)
yay 12.5.7-1                         (AUR helper)
```

### 2.20 Services (Enabled at Boot)

**System-level (systemctl enabled):**
```
accounts-daemon.service      — Account management
asusd.service                — ASUS ROG hardware control (laptop)
bluetooth.service            — Bluetooth stack
colord.service               — Color management
containerd.service           — Container runtime (docker dependency)
cups.service                 — Print scheduler
dbus-broker.service          — D-Bus message bus
docker.service               — Container engine
firewalld.service            — Firewall
gdm.service                  — Display manager
grub-btrfsd.service          — Snapshot-aware GRUB menu
NetworkManager.service       — Network management
nvidia-powerd.service        — NVIDIA power management (laptop GPU)
ollama.service               — LLM server
polkit.service               — Authorization manager
power-profiles-daemon.service — Power profiles (laptop)
rtkit-daemon.service         — Realtime scheduling
supergfxd.service            — GPU switching (laptop)
systemd-journald.service     — Journal (default)
systemd-logind.service       — Session management (default)
systemd-timesyncd.service    — NTP sync
systemd-udevd.service        — Device management (default)
udisks2.service              — Disk management
upower.service               — Power management
wpa_supplicant.service       — WiFi auth
```

**User-level (systemctl --user enable):**
```
pipewire.service             — Audio session
pipewire-pulse.service       — PulseAudio compat
wireplumber.service          — Session/policy manager
```

### 2.21 dotfiles

**~/.bashrc:**
- Color aliases for `ls` and `grep`
- PS1 prompt: `[user@host shortpath]$`
- NVM (Node Version Manager) initialization
- opencode PATH export
- conda/mambaforge initialization
- Antigravity CLI PATH
- .NET SDK PATH and DOTNET_ROOT
- OpenMono.ai PATH
- Custom functions: `explain()` (LLM-based command explanation), `diagnose()` (log analysis)
- Aliases: `ai` → opencode, `ai-mono` → openmono, `ai-status` → agent status

**~/.bash_profile:**
- Sources ~/.bashrc
- Sources ~/.local/bin/env
- Antigravity CLI PATH

**~/.gitconfig:**
- GitHub credential helper: `gh auth git-credential`
- User: ShrekDino, email: SamiT2825@synaptechbio.org

---

## 3. Target Machine: Desktop (Shweemier)

### 3.1 Hardware

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 5800X (8C/16T, Zen 3) |
| GPU | NVIDIA GeForce RTX 2080 Super (8 GB, Turing TU104) |
| RAM | 48 GB DDR4 |
| WiFi/BT | Intel AX210 (AX210NGW, WiFi 6E + BT 5.3, iwlwifi driver) |
| Storage | TBD (prompted at install time) |

### 3.2 Operating System Targets

Identical to laptop:
- Arch Linux (rolling)
- linux-zen (primary) + linux-lts (fallback)
- amd-ucode
- `systemd` init

### 3.3 Intended Disk Layout

Same as laptop:
```
DISK
├── DISKp1  vfat  /boot   (1 GB EFI system partition)
└── DISKp2  LVM2_member
    └── ArchinstallVg-root  btrfs
        ├── @      →  /
        ├── @home  →  /home
        ├── @pkg   →  /var/cache/pacman/pkg
        └── @log   →  /var/log
```

### 3.4 Intended Services

Identical to laptop **minus** laptop-specific services:
- Remove: `asusd.service`, `supergfxd.service`, `nvidia-powerd.service`, `power-profiles-daemon.service`
- Keep: All others (gdm, NetworkManager, bluetooth, cups, firewalld, docker, ollama, systemd-timesyncd, grub-btrfsd)

---

## 4. Laptop → Desktop Migration Delta

### 4.1 Removed (ASUS ROG laptop-specific)

| Package | Reason |
|---------|--------|
| asusctl | ASUS ROG hardware controls (keyboard, fans, etc.) — no ASUS motherboard |
| rog-control-center | GUI for ASUS ROG settings |
| supergfxctl | GPU switching (integrated/discrete) — desktop has one GPU |
| power-profiles-daemon | Power state management — desktop doesn't need battery optimization |
| g14 repo | ASUS Linux repository in pacman.conf |

| Service | Reason |
|---------|--------|
| asusd.service | No ASUS ROG hardware |
| supergfxd.service | No GPU switching needed |
| nvidia-powerd.service | Desktop GPU power management not needed |
| power-profiles-daemon.service | No battery on desktop |

### 4.2 Changed

| Setting | Laptop | Desktop |
|---------|--------|---------|
| Hostname | Shweem | Shweemier |
| GPU driver | nvidia-open-dkms (RTX 3060 laptop) | nvidia-open-dkms (RTX 2080 Super) — same driver, both Turing+ |
| WiFi driver | mt7921e (MediaTek) | iwlwifi (Intel AX210) — both in linux-firmware |
| CPU microcode | amd-ucode | amd-ucode (same) |

### 4.3 Kept Identical

- **Kernel**: linux-zen + linux-lts
- **Disk layout**: LVM → btrfs subvolumes
- **Filesystem options**: compress=zstd:3, ssd, discard=async
- **Bootloader**: GRUB + grub-btrfs
- **Desktop**: GNOME 50 + GDM
- **Audio**: PipeWire + WirePlumber
- **Network**: NetworkManager + wpa_supplicant + bluetooth
- **Firewall**: firewalld
- **Printing**: cups
- **GPU stack**: nvidia-open-dkms + libva-nvidia-driver + nvidia-container-toolkit
- **Container**: docker + nvidia-container-runtime
- **AI/ML**: ollama
- **AUR helper**: yay
- **AUR packages**: miniconda3, pamac-aur, signal-cli, tetrd, appimagelauncher
- **Swap**: zram-generator with zstd
- **Snapshots**: snapper + grub-btrfs
- **All GNOME apps**, utilities, dev tools
- **User**: cinni (UID 1000), wheel sudo
- **Locale**: en_US.UTF-8
- **Timezone**: America/Chicago
- **Keymap**: us

---

## 5. Repository Structure

```
arch-desktop-setup/
├── install.sh                  Main installer script (bash) — ~846 lines
├── finish_setup.sh             Post-install script (AUR cache install, bash fix)
├── README.md                   Quick-start usage guide
├── PROJECT_DOCS.md             This file — full project documentation
├── .gitignore                  Ignores swap files, .DS_Store
├── packages/                   Package lists — organized into subdirectories
│   ├── core.txt                Base system + kernel + bootloader (always installed)
│   ├── network.txt             NetworkManager + bluetooth + firewalld (always)
│   ├── audio.txt               PipeWire + WirePlumber (always)
│   ├── printing.txt            CUPS printing (extra category)
│   ├── development.txt         Docker + ollama + dev tools (extra category)
│   ├── utilities.txt           CLI utilities + zram + snapper (extra category)
│   ├── aur.txt                 AUR packages (extra category)
│   ├── firmware/
│   │   ├── amd-cpu.txt         amd-ucode (auto-detected)
│   │   └── intel-cpu.txt       intel-ucode (auto-detected)
│   ├── drivers/
│   │   ├── nvidia.txt          nvidia-open-dkms + container runtime (auto-detected)
│   │   ├── amd-gpu.txt         mesa + vulkan-radeon (auto-detected)
│   │   ├── intel-gpu.txt       mesa + vulkan-intel (auto-detected)
│   │   └── vm.txt              VirtualBox/QEMU guest tools (auto-detected)
│   └── desktops/
│       ├── common.txt          Fonts + gvfs + xdg-utils (shared by any DE)
│       ├── gnome.txt           Full GNOME 50 + dash-to-panel + appindicator
│       └── kde.txt             Plasma-desktop + Dolphin + Konsole + Kate
├── configs/                    System configuration files
│   ├── mkinitcpio.conf         Initramfs hooks and compression (base config)
│   ├── pacman.conf             Package manager config (ILoveCandy, multilib)
│   ├── zram-generator.conf     ZRAM swap config (zstd compression)
│   ├── modprobe.d/
│   │   └── nvidia.conf         NVIDIA kernel module options
│   ├── docker/
│   │   └── daemon.json         Docker runtime config (nvidia)
│   └── NetworkManager/
│       └── conf.d/
│           └── 00-config.conf  NM unmanaged interfaces (tun*)
└── dotfiles/                   User dotfiles
    ├── bashrc                  Shell configuration
    ├── bash_profile            Login shell config
    └── gitconfig               Git identity + credential helper
```

### 5.1 File Annotations

#### install.sh
- **Role**: The single entry point. Boot Arch ISO, run this, get a complete system.
- **Language**: Pure bash with `set -euo pipefail` for safety.
- **Structure**: Function-based with a `main()` orchestrator at the bottom.
- **Interactivity**: Prompts for disk selection, plan review confirmation, and passwords.
- **Size**: ~846 lines.

#### packages/ (15 files)
- **Format**: One package name per line. Lines starting with `#` are comments. Blank lines ignored.
- **Resolution**: The `build_install_list()` function dynamically assembles an `INSTALL_LIST` array based on:
  - **Always**: `core.txt`, `network.txt`, `audio.txt`
  - **Auto-detected**: `firmware/amd-cpu.txt` or `firmware/intel-cpu.txt` (CPU vendor)
  - **Auto-detected**: `drivers/nvidia.txt`, `drivers/amd-gpu.txt`, or `drivers/intel-gpu.txt` (GPU vendor)
  - **Auto-detected**: `drivers/vm.txt` (if running in a VM)
  - **User choice**: `desktops/common.txt` + `desktops/gnome.txt` or `desktops/kde.txt` (DE)
  - **Profile-based**: `printing.txt`, `development.txt`, `utilities.txt`, `aur.txt` (Full profile or user-selectable in Custom)
- **Idempotent**: `pacman -S --needed` skips already-installed packages, safe for re-runs.

#### configs/ (7 files)
- System configuration files that are copied into `/mnt/etc/` during install.
- GPU-specific configs (nvidia modprobe, docker daemon) are only copied if the matching GPU vendor was detected.

#### dotfiles/ (3 files)
- User-level config files (bashrc, bash_profile, gitconfig). Copied to the prompted user's home directory during install.

---

## 6. Install Script Walkthrough

The script has been rewritten as an interactive, hardware-aware installer. The architecture follows a pipeline: **detect → prompt → build → review → execute**.

### 6.1 Global Setup

- `set -euo pipefail`: Strict error handling (exit on error, unset variable error, pipe failure).

**Configuration variables**: Defaults for hostname, username, locale, timezone, keymap, disk layout (VG `ArchinstallVg`, LV `root`, btrfs options with zstd compression).

**Hardware globals**: `CPU_VENDOR`, `GPU_VENDOR`, `VM_TYPE`, `TOTAL_RAM` are auto-detected at runtime.

**Build list**: `INSTALL_LIST` is an array of `label:path` entries dynamically built by `build_install_list()`.

### 6.2 preflight()

Identical to previous version — checks UEFI mode, internet connectivity, package definitions exist, and unmounts stale `/mnt`.

### 6.3 detect_hardware() — New

Reads `/proc/cpuinfo` for CPU vendor (AMD/Intel), `lspci` for GPU vendor (NVIDIA/AMD/Intel), `systemd-detect-virt` for VM detection, and `/proc/meminfo` for total RAM. Sets the respective global variables.

### 6.4 select_disk()

Unchanged from previous version — lists available disks, prompts user, validates input, sets `EFI_PART` and `LVM_PART`.

### 6.5 prompt_config() — New

Interactive questionnaire that collects all user preferences before any disk operations:

| Prompt | Variable | Default |
|--------|----------|---------|
| Hostname | `HOSTNAME` | archbox |
| Username | `USERNAME` | cinni |
| Locale | `LOCALE` | en_US.UTF-8 (auto-detected) |
| Timezone | `TIMEZONE` | auto-detected via `timedatectl` |
| Keymap | `KEYMAP` | us |
| LUKS encryption | `LUKS_ENCRYPT` | false |
| Desktop environment | `DESKTOP_CHOICE` | gnome (kde/cli options) |
| Install profile | `PROFILE` | full (minimal/custom options) |

### 6.6 build_install_list() — New

Dynamically builds `INSTALL_LIST` based on:

1. **Always**: core, network, audio
2. **Auto-detected (CPU)**: firmware/amd-cpu.txt or firmware/intel-cpu.txt
3. **Auto-detected (GPU)**: drivers/nvidia.txt, drivers/amd-gpu.txt, or drivers/intel-gpu.txt
4. **Auto-detected (VM)**: drivers/vm.txt (if in a VM)
5. **User choice**: desktops/common.txt + desktops/gnome.txt or desktops/kde.txt
6. **Profile-based extras**:
   - Full: printing + development + utilities + AUR
   - Minimal: none (base + desktop only)
   - Custom: calls `prompt_custom_extras()` which shows each category's packages and asks Y/n

### 6.7 prompt_custom_extras() — New

For the Custom profile, iterates over each extra category (printing, development, utilities, AUR), shows up to 5 packages in each, and asks `Include? [Y/n]`. Answers build the `INSTALL_LIST`.

### 6.8 print_plan()

Updated to show dynamic content:
- Target disk and partitioning (shows `LUKS →` prefix if encryption enabled)
- System identity (uses prompted values)
- Auto-detected hardware summary
- Packages by category (reads from `INSTALL_LIST`)
- Services to enable (varies by desktop choice and extras selected)

Still prompts `Proceed with installation? [Y/n]` before any destructive actions.

### 6.9 partition_disk()

Unchanged — creates GPT partitions (1 GB EFI + rest for LVM). EFI partition is formatted as FAT32 immediately.

### 6.10 setup_encryption() — New

Only runs if `LUKS_ENCRYPT=true`. Executes `cryptsetup luksFormat` and `cryptsetup open` on the LVM partition, then replaces `LVM_PART` with `/dev/mapper/cryptroot` for subsequent LVM operations.

### 6.11 setup_lvm_btrfs()

Unchanged — creates LVM PV/VG/LV, formats as btrfs, creates subvolumes.

### 6.12 mount_all()

Unchanged — mounts btrfs subvolumes and EFI partition.

### 6.13 install_base()

Updated to use auto-detected CPU microcode. The pacstrap command now includes `cryptsetup` (needed if LUKS is selected, harmless otherwise):

```bash
local cpu_ucode=""
if [[ "$CPU_VENDOR" == "amd" ]]; then cpu_ucode="amd-ucode"
elif [[ "$CPU_VENDOR" == "intel" ]]; then cpu_ucode="intel-ucode"
fi

pacstrap -K /mnt base base-devel linux-zen linux-zen-headers \
    linux-firmware $cpu_ucode btrfs-progs lvm2 sudo vim nano \
    bash-completion git wget grub efibootmgr grub-btrfs snapper \
    cryptsetup
```

### 6.14 generate_fstab()

Unchanged.

### 6.15 configure_system()

Unchanged in structure, but uses prompted values (hostname, username, locale, timezone, keymap) instead of hardcoded ones.

### 6.16 configure_initramfs() — Updated

Dynamically builds the mkinitcpio hook list. If LUKS is enabled, the `encrypt` hook is inserted:

```bash
local hooks="base udev autodetect microcode modconf kms keyboard keymap consolefont"

if [[ "$LUKS_ENCRYPT" == true ]]; then
    hooks="$hooks block encrypt lvm2 filesystems fsck"
else
    hooks="$hooks block lvm2 filesystems fsck"
fi
```

The config is written directly to `/mnt/etc/mkinitcpio.conf` via a heredoc (not copied from the configs directory, since it's now dynamic).

### 6.17 install_grub() — Updated

Now dynamically builds GRUB config:

- `GRUB_CMDLINE_LINUX_DEFAULT` includes `cryptdevice=...` if LUKS is enabled
- `GRUB_ENABLE_CRYPTODISK` is set to `y` if LUKS
- Config is written directly via heredoc to `/mnt/etc/default/grub`

### 6.18 setup_users()

Same as before — prompts for root and user passwords, creates user with sudo. Uses the prompted `USERNAME` variable.

### 6.19 install_all_packages() — Updated

Iterates over `INSTALL_LIST` and installs each category via `pacman -S --noconfirm --needed`. Skips the AUR label (handled separately).

### 6.20 copy_configs() — Updated

Conditionally copies GPU-specific configs:
- NVIDIA modprobe config only if `GPU_VENDOR=nvidia`
- Docker daemon config only if `GPU_VENDOR=nvidia`
- Always copies: pacman.conf, zram-generator.conf, NetworkManager config

### 6.21 enable_services() — Updated

Dynamically enables services based on choices:
- `gdm.service` for GNOME, `sddm.service` for KDE
- Always: NetworkManager, bluetooth, firewalld, timesyncd
- Conditional: cups (if printing selected), docker (if development selected)

### 6.22 copy_dotfiles()

Same as before — copies bashrc, bash_profile, gitconfig to the prompted username's home.

### 6.23 install_aur() — Updated

Only runs if `AUR_ENABLED=true` (which is true for Full profile, or if user selected AUR in Custom profile). Builds yay from source (same process as before), then installs packages from `aur.txt`.

### 6.24 print_done()

Updated to show dynamic information — hostname, username, disk, desktop choice, GPU vendor, LUKS status.

### 6.25 main()

```bash
main() {
    preflight              # 1. Check UEFI, internet, packages
    detect_hardware        # 2. Auto-detect CPU, GPU, VM, RAM
    select_disk            # 3. Choose target disk
    prompt_config          # 4. Interactive questionnaire
    build_install_list     # 5. Build package list from choices
    print_plan             # 6. Show plan and confirm

    partition_disk         # 7. Wipe and partition
    setup_encryption       # 8. LUKS (if selected)
    setup_lvm_btrfs        # 9. LVM + btrfs subvolumes
    mount_all              # 10. Mount filesystem tree
    install_base           # 11. pacstrap base packages
    generate_fstab         # 12. Generate /etc/fstab
    configure_system       # 13. Timezone, locale, hostname
    configure_initramfs    # 14. mkinitcpio (dynamic hooks)
    install_grub           # 15. GRUB (dynamic cryptdevice)
    setup_users            # 16. Root + user + sudo
    install_all_packages   # 17. Dynamic package installation
    copy_configs           # 18. System configs
    enable_services        # 19. Dynamic service enabling
    copy_dotfiles          # 20. User dotfiles
    install_aur            # 21. yay + AUR (conditional)

    print_done             # 22. Summary + next steps
}

main
```

---

## 7. Package Lists

### 7.1 core.txt — Base System (19 packages)

Always installed. Base system, kernel (lts included as fallback), bootloader, filesystem tools, editors, git.

```bash
base, base-devel, linux-zen, linux-zen-headers, linux-lts, linux-lts-headers
linux-firmware, btrfs-progs, lvm2, dkms
grub, efibootmgr, grub-btrfs
sudo, vim, nano, bash-completion, wget, git
```

Note: CPU microcode (`amd-ucode` / `intel-ucode`) is no longer in core — it's auto-detected and installed from `firmware/`.

### 7.2 firmware/*.txt — CPU Microcode (auto-detected)

| File | Condition | Package |
|------|-----------|---------|
| `firmware/amd-cpu.txt` | CPU vendor = AMD | `amd-ucode` |
| `firmware/intel-cpu.txt` | CPU vendor = Intel | `intel-ucode` |

Installed during `pacstrap` via the `install_base()` function, which reads CPU vendor from `/proc/cpuinfo`.

### 7.3 drivers/*.txt — GPU Drivers (auto-detected)

| File | Condition | Packages |
|------|-----------|----------|
| `drivers/nvidia.txt` | NVIDIA GPU | `nvidia-open-dkms`, `libva-nvidia-driver`, `nvidia-container-toolkit` |
| `drivers/amd-gpu.txt` | AMD GPU | `mesa`, `vulkan-radeon`, `libva-mesa-driver`, `mesa-vdpau` |
| `drivers/intel-gpu.txt` | Intel GPU | `mesa`, `vulkan-intel`, `intel-media-driver`, `libva-intel-driver` |
| `drivers/vm.txt` | Running in VM | `virtualbox-guest-utils`, `spice-vdagent`, `qemu-guest-agent` |

**NVIDIA rationale**: `nvidia-open-dkms` is the official open-source kernel module supporting Turing (RTX 2000) and newer. `libva-nvidia-driver` bridges VA-API to NVIDIA's VDPAU for hardware video decoding in browsers and media apps. `nvidia-container-toolkit` enables GPU passthrough to Docker.

**AMD rationale**: `mesa` provides OpenGL/Vulkan via RADV. `vulkan-radeon` is the official AMD Vulkan driver. `libva-mesa-driver` handles VA-API video decode. `mesa-vdpau` provides VDPAU for older video apps.

**Intel rationale**: Same Mesa for OpenGL/Vulkan. `intel-media-driver` is the modern VA-API driver for Gen8+ GPUs; `libva-intel-driver` covers older hardware.

### 7.4 desktops/*.txt — Desktop Environments (user chosen)

| File | Contents | Size |
|------|----------|------|
| `desktops/common.txt` | Shared DE packages (fonts, gvfs, xdg-utils, adwaita) | 8 pkgs |
| `desktops/gnome.txt` | Full GNOME 50 + dash-to-panel + appindicator | 60 pkgs |
| `desktops/kde.txt` | Plasma-desktop + curated apps (Dolphin, Konsole, Kate, Gwenview, etc.) | 15 pkgs |

**KDE curated approach**: Unlike `plasma-meta` which pulls every KDE app, the kde.txt file contains only `plasma-desktop` plus hand-picked core apps:
  - `plasma-wayland-session` (Wayland session)
  - `plasma-nm`, `plasma-pa` (NetworkManager/audio applets)
  - `kde-gtk-config`, `breeze-gtk` (GTK integration)
  - `sddm` (display manager)
  - `konsole`, `dolphin`, `kate`, `gwenview`, `spectacle`, `okular`, `ark`, `kcalc`

### 7.5 network.txt — Networking (6 packages)

Always installed.

```bash
networkmanager, network-manager-applet, wpa_supplicant
bluez, bluez-utils, firewalld
```

### 7.6 audio.txt — Audio (8 packages)

Always installed.

```bash
pipewire, pipewire-alsa, pipewire-jack, pipewire-pulse
wireplumber, gst-plugin-pipewire, libpulse, sof-firmware
```

### 7.7 printing.txt — CUPS Printing (3 packages)

Extra category — installed with Full profile or user-selectable in Custom.

```bash
cups, cups-pk-helper, system-config-printer
```

### 7.8 development.txt — Development Tools (10 packages)

Extra category — installed with Full profile or user-selectable in Custom.

```bash
cmake, docker, github-cli, htop, inotify-tools
nvm, ollama, python-pipx, ripgrep, smartmontools
```

### 7.9 utilities.txt — CLI Utilities (8 packages)

Extra category — installed with Full profile or user-selectable in Custom.

```bash
btop, fastfetch, fuse2, snapper
zram-generator, cliphist, wl-clipboard, wl-clip-persist
```

Note: `xdg-utils` and `xdg-user-dirs-gtk` moved to `desktops/common.txt` since they're desktop-environment dependencies.

### 7.10 aur.txt — AUR Packages (5 packages)

Extra category — installed with Full profile or user-selectable in Custom. yay is built from source before these are installed.

```bash
pamac-aur, signal-cli, tetrd, appimagelauncher, miniconda3
```

---

## 8. Configuration Files

### 8.1 mkinitcpio.conf

**Purpose**: Controls the initramfs (initial RAM filesystem) — what modules and hooks are included for early boot.

**Note**: This config is **generated dynamically** by `configure_initramfs()` at install time. The hook list varies based on the LUKS choice.

**Without LUKS** (default):
```bash
HOOKS=(base udev autodetect microcode modconf kms keyboard keymap consolefont block lvm2 filesystems fsck)
```

**With LUKS** (if user selects encryption):
```bash
HOOKS=(base udev autodetect microcode modconf kms keyboard keymap consolefont block encrypt lvm2 filesystems fsck)
```

Hook explanations:
- `base`: Sets up early userspace (devtmpfs, console, basic tools)
- `udev`: Device detection and module loading
- `autodetect`: Reduces initramfs size by only including modules for detected hardware
- `microcode`: Applies AMD/Intel CPU microcode update early in boot
- `modconf`: Loads modprobe configuration files
- `kms`: Kernel Mode Setting — enables early framebuffer for smooth boot
- `keyboard`, `keymap`, `consolefont`: Console input support (needed for LUKS password entry)
- `block`: Detects and loads block device drivers
- `encrypt`: Unlocks LUKS-encrypted root volume at boot (only present when LUKS enabled)
- `lvm2`: Activates LVM volume groups and logical volumes
- `filesystems`: Mounts root filesystem
- `fsck`: Filesystem check before mount

**Compression**: `COMPRESSION="zstd"` — fast decompression, small image size.

### 8.2 pacman.conf

**Purpose**: Package manager configuration.

Key settings:
- `Color`: Colorized output
- `ILoveCandy`: Pacman progress bar uses candy animation
- `ParallelDownloads = 5`: Download 5 packages simultaneously
- `DownloadUser = alpm`: Run downloads as unprivileged `alpm` user
- `SigLevel = Required DatabaseOptional`: Require package signatures, but database signatures optional
- `LocalFileSigLevel = Optional`: Local package installs don't require signatures
- `[multilib]` enabled: 32-bit library support (needed for Steam, Wine, etc.)

Note: The `[g14]` ASUS Linux repository from the laptop is **not** included.

### 8.3 zram-generator.conf

**Purpose**: Configure zram (compressed RAM-based swap) via systemd.

```ini
[zram0]
compression-algorithm = zstd
```

This creates a zram device (compressed swap in RAM) using zstd compression. No size is specified — zram-generator defaults to `min(ram, 8GB) / 2` for zram0. On a 48 GB system, this gives ~24 GB of compressed swap equivalent (but actual RAM used is minimal due to compression).

### 8.4 nvidia.conf (modprobe.d)

**Purpose**: NVIDIA kernel module parameters.

```
options nvidia NVreg_UseKernelSuspendNotifiers=1
options nvidia NVreg_TemporaryFilePath=/var/tmp
blacklist nouveau
```

- `NVreg_UseKernelSuspendNotifiers=1`: Uses kernel's suspend/resume notifiers instead of the old PCI PM method — faster and more reliable suspend/wake.
- `NVreg_TemporaryFilePath=/var/tmp`: Stores NVIDIA temporary files on disk (not tmpfs in RAM) to avoid memory pressure during driver operations.
- `blacklist nouveau`: Prevents the open-source nouveau driver from loading, ensuring nvidia-open-dkms is used.

### 8.5 docker/daemon.json

**Purpose**: Docker daemon configuration — enables NVIDIA GPU acceleration in containers.

```json
{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```

This registers the `nvidia` runtime. Containers started with `--runtime=nvidia` (or via `nvidia-container-toolkit`) get GPU access. The `nvidia-container-runtime` binary is provided by the `nvidia-container-toolkit` package.

### 8.6 NetworkManager/conf.d/00-config.conf

**Purpose**: Mark certain interfaces as unmanaged by NetworkManager.

```ini
[keyfile]
unmanaged-devices=interface-name:tun*
```

Interfaces matching `tun*` (tunnel interfaces, e.g., from Tetrd, OpenVPN, WireGuard tunnels managed by other tools) are ignored by NetworkManager. This prevents NM from interfering with tunnel connections.

### 8.7 GRUB Defaults

**Purpose**: GRUB bootloader configuration.

**Note**: This config is **generated dynamically** by `install_grub()` at install time. The kernel command line varies based on the LUKS choice.

**Without LUKS** (default):
```bash
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="Arch"
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"
GRUB_CMDLINE_LINUX=""
GRUB_PRELOAD_MODULES="part_gpt part_msdos"
GRUB_TIMEOUT_STYLE=menu
GRUB_TERMINAL_INPUT=console
GRUB_GFXMODE=auto
GRUB_GFXPAYLOAD_LINUX=keep
GRUB_DISABLE_RECOVERY=true
GRUB_ENABLE_CRYPTODISK=n
```

**With LUKS** (if user selects encryption):
```bash
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="Arch"
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet cryptdevice=${LVM_PART}:cryptroot root=/dev/mapper/${VG_NAME}-${LV_NAME}"
GRUB_CMDLINE_LINUX=""
GRUB_PRELOAD_MODULES="part_gpt part_msdos"
GRUB_TIMEOUT_STYLE=menu
GRUB_TERMINAL_INPUT=console
GRUB_GFXMODE=auto
GRUB_GFXPAYLOAD_LINUX=keep
GRUB_DISABLE_RECOVERY=true
GRUB_ENABLE_CRYPTODISK=y
```

Key differences:
- `GRUB_CMDLINE_LINUX_DEFAULT` includes `cryptdevice=...` kernel parameter when LUKS is selected
- `GRUB_ENABLE_CRYPTODISK=y` enables reading from LUKS volumes at boot menu time

---

## 9. Dotfiles

### 9.1 .bashrc

```
[[ $- != *i* ]] && return           # Skip if non-interactive

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '                # [user@host shortpath]$

export NVM_DIR="$HOME/.nvm"        # Node Version Manager
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

[ -f /opt/miniconda3/etc/profile.d/conda.sh ] && source /opt/miniconda3/etc/profile.d/conda.sh

export PATH="$HOME/.opencode/bin:$PATH"   # opencode CLI
export PATH="$HOME/.local/bin:$PATH"      # Antigravity CLI
export DOTNET_ROOT="$HOME/.dotnet"        # .NET SDK
export PATH="$DOTNET_ROOT:$PATH"
export PATH="$HOME/openmono.ai:$PATH"     # OpenMono.ai
```

**Note**: The laptop's `.bashrc` contained AI companion functions (`explain()`, `diagnose()`). These are omitted from the installer dotfiles because they are environment-specific and will be re-created when the user sets up their tools post-install. Conda initialization is included by default when `miniconda3` is selected in the AUR packages.

### 9.2 .bash_profile

```
[[ -f ~/.bashrc ]] && . ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
```

### 9.3 .gitconfig

```ini
[credential "https://github.com"]
    helper =
    helper = !/usr/bin/gh auth git-credential
[credential "https://gist.github.com"]
    helper =
    helper = !/usr/bin/gh auth git-credential
[user]
    email = SamiT2825@synaptechbio.org
    name = ShrekDino
```

GitHub authentication uses `gh` CLI credential helper. The user will need to run `gh auth login` post-install to authenticate.

---

## 10. Usage Instructions

### 10.1 Prerequisites

- Arch Linux live ISO (booted in UEFI mode)
- Internet connection (wired or WiFi)
- Target disk ready (will be completely wiped)

### 10.2 Recommended Method: git clone

```bash
# From the Arch live ISO, connect to the internet then:
pacman -Sy git --noconfirm
git clone https://github.com/ShrekDino/arch-desktop-setup.git
cd arch-desktop-setup && bash install.sh
```

### 10.3 Alternative: curl to bash

```bash
curl -sL https://raw.githubusercontent.com/ShrekDino/arch-desktop-setup/master/install.sh | bash
```

### 10.4 User Prompts During Install

The script collects all preferences up front, then shows a plan summary before making any changes:

1. **Hardware detection** — CPU, GPU, RAM are displayed (automatic)
2. **Disk selection** — Type the full path (e.g., `/dev/nvme0n1`)
3. **System config** — Hostname, username, locale, timezone, keymap, LUKS encryption
4. **Desktop choice** — GNOME, KDE, or CLI-only
5. **Profile selection** — Full, Minimal, or Custom (browse packages per category)
6. **Plan review** — Full summary with package counts, then `Proceed? [Y/n]`
7. **Passwords** — Root password and user password (interactive, during chroot)

### 10.5 Post-Install

```bash
# Unmount and reboot
umount -R /mnt
reboot

# After first login, authenticate GitHub
gh auth login

# Optional: update everything
sudo pacman -Syu
yay -Syu
```

---

## 11. Customization Guide

### 11.1 Default Values (Hostname, User, Locale, etc.)

These are no longer hardcoded — the script prompts for them interactively. If you want different defaults, edit the `prompt_default()` calls in the `prompt_config()` function:

```bash
# In prompt_config():
prompt_default HOSTNAME "Hostname" "archbox"        # Change "archbox" to your default
prompt_default USERNAME "Username" "cinni"           # Change "cinni" to your default
prompt_default LOCALE "Locale" "en_US.UTF-8"         # Change locale default
```

### 11.2 Different Disk Layout

The script uses LVM → btrfs subvolumes with optional LUKS. LUKS is toggled via the interactive prompt. To change layout fundamentally:

- **No LVM (btrfs directly on partition)**: Replace `setup_lvm_btrfs()` with direct partition format and subvolume creation. Remove LVM packages from `core.txt`.
- **Ext4 instead of btrfs**: Replace `mkfs.btrfs` with `mkfs.ext4`, remove subvolume logic, remove `btrfs-progs` from `core.txt`.

### 11.3 Different GPU

The script auto-detects GPU and installs the correct driver package file. To customize:

- Edit `packages/drivers/nvidia.txt` for NVIDIA packages
- Edit `packages/drivers/amd-gpu.txt` for AMD packages  
- Edit `packages/drivers/intel-gpu.txt` for Intel packages
- Add a new file (e.g., `packages/drivers/hybrid.txt`) and add detection logic in `build_install_list()`

### 11.4 Add/Remove Package Categories

Package files live under `packages/` and are loaded dynamically:

- **Add a new file**: Create `packages/gaming.txt` with Steam, Lutris, etc. Then add logic in `build_install_list()` or `prompt_custom_extras()` to include it.
- **Remove a category**: Delete its `.txt` file or skip it in `build_install_list()`.
- **Edit a category**: Just edit the `.txt` file — add/remove lines.

### 11.5 Add a New Desktop Environment

1. Create `packages/desktops/xfce.txt` with XFCE packages
2. In `prompt_config()`, add option `4) XFCE`
3. In `build_install_list()`, add the condition for `DESKTOP_CHOICE="xfce"`
4. In `enable_services()`, add `lightdm.service` (or whatever DM XFCE uses)

---

## 12. Key Design Decisions

### 12.1 Why LVM + btrfs instead of btrfs directly?

The laptop uses LVM even though there's only one volume group with one logical volume. This adds a thin abstraction layer that makes resizing and future reorganization easier without repartitioning. For example, adding a separate `/var` LV or shrinking the root LV to make room for a dual-boot partition is trivial with LVM.

### 12.2 Why zram instead of swap partition?

Zram provides compressed swap in RAM. For a system with 48 GB of RAM, a traditional swap partition would rarely be touched. Zram uses no disk space, provides faster swap (RAM speed), and the zstd compression gives ~2-3x effective capacity. On desktop workloads, this is purely a safety net against OOM.

### 12.3 Why GRUB instead of systemd-boot?

GRUB supports btrfs snapshots via `grub-btrfs`, which automatically adds snapshot entries to the boot menu. systemd-boot doesn't have this integration. GRUB also handles LVM and btrfs without manual configuration.

### 12.4 Why does the mkinitcpio include keyboard/keymap hooks?

The hooks `keyboard`, `keymap`, and `consolefont` are **always** included regardless of LUKS choice. They enable keyboard input during early boot and are harmless when not needed. If LUKS is selected, the `encrypt` hook is also added for passphrase entry. The overhead is negligible (a few KB in the initramfs).

### 12.5 Why nvidia-open-dkms instead of nvidia (closed-source)?

The `nvidia-open-dkms` package provides NVIDIA's open kernel modules for Turing (RTX 2000) and newer GPUs. The RTX 2080 Super is Turing TU104. Advantages:
- Open source (can inspect/modify)
- DKMS rebuilds on kernel updates automatically
- Same performance as closed-source for Turing+

The `nvidia` (closed-source) package would also work, but the open module is the future direction from NVIDIA.

### 12.6 Why pacman packages in txt files instead of arrays in the script?

Separating package lists from logic allows:
- Easy editing without touching the install script
- Clear category organization
- Simple counting and reporting
- Future automation (e.g., generate the lists from `pacman -Qe`)

### 12.7 Why not use archinstall?

`archinstall` is generic and provides a menu-driven selection process at install time. This project offers:
- **Pre-selected, curated package lists** organized by category that can be reviewed and edited before running
- **Hardware-aware auto-detection** — correct drivers and microcode selected without user knowledge
- **Three install profiles** — Full, Minimal, and Custom (browse each category)
- **Multiple desktop environments** — GNOME and KDE with curated package sets
- **Config files and dotfiles** tracked in version control alongside the install script
- **Idempotent runs** — safe to re-run, packages marked `--needed` won't reinstall

---

## Appendix A: Common Post-Install Tasks

### A.1 GitHub Authentication
```bash
gh auth login
# Follow prompts to authenticate via browser or token
```

### A.2 Install Node.js via NVM
```bash
nvm install --lts
nvm use --lts
```

### A.3 Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### A.4 Update All Packages
```bash
sudo pacman -Syu
yay -Syu
```

### A.5 Configure Snapper
```bash
# Snapshots are pre-configured for / and /home
# To take a manual snapshot:
sudo snapper -c root create -d "before-update"

# To list snapshots:
sudo snapper -c root list
```

---

## Appendix B: Troubleshooting

### B.1 `pacman` conflict stops the installer mid-way

If the installer fails with `unresolvable package conflicts detected` (e.g., `pipewire-jack` vs `jack2`), the base system and disk are safe. Recover by:

```bash
# 1. Mount the partitions from the live ISO
mount -o subvol=@ /dev/mapper/ArchinstallVg-root /mnt
mount /dev/nvme1n1p1 /mnt/boot
arch-chroot /mnt

# 2. Resolve the conflict manually
pacman -S pipewire-jack
# Answer 'y' when prompted to remove jack2

# 3. Continue the remaining install steps from where it failed
# e.g., install remaining packages:
# pacman -S --needed $(cat /root/arch-desktop-setup/packages/audio.txt | tr '\n' ' ')

# 4. Exit and reboot
exit
reboot
```

### B.2 Script fails with SQUASHFS or EXT4-fs error on EFI partition

The EFI partition was not formatted as FAT32 before mounting. This was a bug in earlier versions fixed by moving `mkfs.fat -F32` into `partition_disk()`. Ensure you're on the latest commit.

### B.3 Network not working in live ISO

```bash
# Check interface
ip link

# Connect via WiFi
iwctl --passphrase <pass> station wlan0 connect <SSID>

# Verify
ping archlinux.org
```

---

*End of Project Documentation*
