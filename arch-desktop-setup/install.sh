#!/usr/bin/env bash
#
# Arch Linux Interactive Installer
# =================================
# Run this from the Arch Linux live ISO.
# Detects your hardware, asks what you want, and installs everything.
#
# Recommended:
#   pacman -Sy git --noconfirm
#   git clone https://github.com/ShrekDino/arch-desktop-setup.git
#   cd arch-desktop-setup && bash install.sh
#
# Quick alternative:
#   curl -sL https://raw.githubusercontent.com/ShrekDino/arch-desktop-setup/master/install.sh | bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGES_DIR="$SCRIPT_DIR/packages"
CONFIGS_DIR="$SCRIPT_DIR/configs"
DOTFILES_DIR="$SCRIPT_DIR/dotfiles"

VG_NAME="ArchinstallVg"
LV_NAME="root"
BTRFS_OPTS="rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2"

# Hardware (auto-detected)
CPU_VENDOR=""
GPU_VENDOR=""
VM_TYPE="none"
TOTAL_RAM=0

# User config (prompted)
DISK=""
EFI_PART=""
LVM_PART=""
HOSTNAME="archbox"
USERNAME="cinni"
LOCALE="en_US.UTF-8"
TIMEZONE="America/Chicago"
KEYMAP="us"
FONT="default8x16"
LUKS_ENCRYPT=false
DESKTOP_CHOICE="gnome"
PROFILE="full"

# Build list
INSTALL_LIST=()
AUR_ENABLED=false

# ──────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────

count_packages() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo 0
        return
    fi
    grep -v '^#' "$file" | grep -v '^$' | wc -l
}

read_packages() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        return
    fi
    grep -v '^#' "$file" | grep -v '^$'
}

count_packages_by_label() {
    local label="$1"
    local total=0
    for entry in "${INSTALL_LIST[@]}"; do
        local entry_label="${entry%%:*}"
        local entry_file="${entry#*:}"
        if [[ "$entry_label" == "$label" ]]; then
            total=$((total + $(count_packages "$entry_file")))
        fi
    done
    echo "$total"
}

# ──────────────────────────────────────────────
# HARDWARE DETECTION
# ──────────────────────────────────────────────

detect_hardware() {
    info "Detecting hardware..."

    # CPU vendor
    local vendor
    vendor=$(grep -m1 vendor_id /proc/cpuinfo | awk '{print $3}')
    case "$vendor" in
        GenuineIntel) CPU_VENDOR="intel" ;;
        AuthenticAMD) CPU_VENDOR="amd" ;;
    esac

    # GPU vendor
    local gpu_info
    gpu_info=$(lspci -nn 2>/dev/null | grep -E 'VGA|3D|Display' | head -1)
    if echo "$gpu_info" | grep -qi nvidia; then
        GPU_VENDOR="nvidia"
    elif echo "$gpu_info" | grep -qi amd; then
        GPU_VENDOR="amd"
    elif echo "$gpu_info" | grep -qi intel; then
        GPU_VENDOR="intel"
    fi

    # Virtualization
    local virt
    virt=$(systemd-detect-virt 2>/dev/null || echo "none")
    if [[ "$virt" != "none" ]]; then
        VM_TYPE="$virt"
    fi

    # RAM
    TOTAL_RAM=$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo)

    echo "  CPU:  $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')"
    echo "  GPU:  $gpu_info"
    echo "  RAM:  ${TOTAL_RAM} MB"
    echo "  VM:   $virt"
    echo
}

# ──────────────────────────────────────────────
# INTERACTIVE PROMPTS
# ──────────────────────────────────────────────

select_disk() {
    echo -e "${YELLOW}Available disks:${NC}"
    lsblk -dno NAME,SIZE,MODEL | awk '{print "  /dev/" $0}'
    echo
    read -r -p "Install to which disk? (e.g. /dev/nvme0n1 or /dev/sda): " DISK

    if [[ ! -b "$DISK" ]]; then
        fail "Block device $DISK does not exist."
    fi

    if mount | grep -q "$DISK"; then
        fail "$DISK appears to be mounted. Unmount first."
    fi

    if [[ "$DISK" =~ nvme ]]; then
        PART_PREFIX="${DISK}p"
    else
        PART_PREFIX="${DISK}"
    fi
    EFI_PART="${PART_PREFIX}1"
    LVM_PART="${PART_PREFIX}2"
}

prompt_default() {
    local var_name="$1"
    local prompt="$2"
    local default="$3"
    local input

    read -r -p "${prompt} [${default}]: " input
    if [[ -z "$input" ]]; then
        printf -v "$var_name" '%s' "$default"
    else
        printf -v "$var_name" '%s' "$input"
    fi
}

prompt_config() {
    echo
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  System Configuration${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo

    prompt_default HOSTNAME "Hostname" "archbox"
    prompt_default USERNAME "Username" "cinni"

    # Locale
    if locale -a 2>/dev/null | grep -qi "en_US.utf8"; then
        LOCALE="en_US.UTF-8"
    fi
    prompt_default LOCALE "Locale" "$LOCALE"

    # Timezone — try to detect
    local detected_tz
    detected_tz=$(timedatectl show 2>/dev/null | grep Timezone | cut -d= -f2 || echo "")
    [[ -n "$detected_tz" ]] && TIMEZONE="$detected_tz"
    prompt_default TIMEZONE "Timezone" "$TIMEZONE"

    prompt_default KEYMAP "Keymap" "$KEYMAP"

    # LUKS
    local luks_input
    read -r -p "Encrypt disk with LUKS? [y/N]: " luks_input
    if [[ "$luks_input" =~ ^[Yy] ]]; then
        LUKS_ENCRYPT=true
    fi

    # Desktop
    echo
    echo "Desktop environment:"
    echo "  1) GNOME  (57 packages — recommended)"
    echo "  2) KDE    (15 packages)"
    echo "  3) CLI    (no graphical desktop)"
    local de_choice
    read -r -p "Select [1]: " de_choice
    case "$de_choice" in
        2) DESKTOP_CHOICE="kde" ;;
        3) DESKTOP_CHOICE="cli" ;;
        *) DESKTOP_CHOICE="gnome" ;;
    esac

    # Profile
    echo
    echo "Install profile:"
    echo "  1) Full     — everything (core + desktop + extras + AUR)"
    echo "  2) Minimal  — base system + drivers + desktop only"
    echo "  3) Custom   — pick each extra category"
    local profile_choice
    read -r -p "Select [1]: " profile_choice
    case "$profile_choice" in
        2) PROFILE="minimal" ;;
        3) PROFILE="custom" ;;
        *) PROFILE="full" ;;
    esac

    echo
}

# ──────────────────────────────────────────────
# PACKAGE RESOLUTION
# ──────────────────────────────────────────────

add_to_install_list() {
    local label="$1"
    local file="$2"
    INSTALL_LIST+=("${label}:${file}")
}

build_install_list() {
    INSTALL_LIST=()

    # Always installed
    add_to_install_list "core" "$PACKAGES_DIR/core.txt"
    add_to_install_list "network" "$PACKAGES_DIR/network.txt"
    add_to_install_list "audio" "$PACKAGES_DIR/audio.txt"

    # CPU microcode (auto-detected)
    if [[ "$CPU_VENDOR" == "amd" ]]; then
        add_to_install_list "firmware" "$PACKAGES_DIR/firmware/amd-cpu.txt"
    elif [[ "$CPU_VENDOR" == "intel" ]]; then
        add_to_install_list "firmware" "$PACKAGES_DIR/firmware/intel-cpu.txt"
    fi

    # GPU drivers (auto-detected)
    if [[ "$GPU_VENDOR" == "nvidia" ]]; then
        add_to_install_list "drivers" "$PACKAGES_DIR/drivers/nvidia.txt"
    elif [[ "$GPU_VENDOR" == "amd" ]]; then
        add_to_install_list "drivers" "$PACKAGES_DIR/drivers/amd-gpu.txt"
    elif [[ "$GPU_VENDOR" == "intel" ]]; then
        add_to_install_list "drivers" "$PACKAGES_DIR/drivers/intel-gpu.txt"
    fi

    # VM guest drivers (auto-detected)
    if [[ "$VM_TYPE" != "none" ]]; then
        add_to_install_list "drivers" "$PACKAGES_DIR/drivers/vm.txt"
    fi

    # Desktop (user choice)
    if [[ "$DESKTOP_CHOICE" != "cli" ]]; then
        add_to_install_list "desktop" "$PACKAGES_DIR/desktops/common.txt"
        if [[ "$DESKTOP_CHOICE" == "gnome" ]]; then
            add_to_install_list "desktop" "$PACKAGES_DIR/desktops/gnome.txt"
        elif [[ "$DESKTOP_CHOICE" == "kde" ]]; then
            add_to_install_list "desktop" "$PACKAGES_DIR/desktops/kde.txt"
        fi
    fi

    # Profile-based extras
    if [[ "$PROFILE" == "full" ]]; then
        add_to_install_list "extras" "$PACKAGES_DIR/printing.txt"
        add_to_install_list "extras" "$PACKAGES_DIR/development.txt"
        add_to_install_list "extras" "$PACKAGES_DIR/utilities.txt"
        AUR_ENABLED=true
    elif [[ "$PROFILE" == "custom" ]]; then
        prompt_custom_extras
    fi
}

prompt_custom_extras() {
    echo
    echo -e "${CYAN}────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}  Custom Selection — Extra Categories${NC}"
    echo -e "${CYAN}────────────────────────────────────────────────${NC}"
    echo

    local categories=(
        "printing:Printing (CUPS)"
        "development:Development tools"
        "utilities:CLI utilities"
        "aur:AUR packages"
    )

    for entry in "${categories[@]}"; do
        local label="${entry%%:*}"
        local display="${entry#*:}"
        local file="$PACKAGES_DIR/${label}.txt"

        if [[ ! -f "$file" ]]; then
            continue
        fi

        local count
        count=$(count_packages "$file")
        echo -e "${YELLOW}${display} (${count} packages):${NC}"
        read_packages "$file" | head -5 | while read -r pkg; do
            echo "    → $pkg"
        done
        local remaining
        remaining=$((count - 5))
        [[ $remaining -gt 0 ]] && echo "    → ... and $remaining more"

        local incl
        read -r -p "  Include? [Y/n]: " incl
        if [[ ! "$incl" =~ ^[Nn] ]]; then
            add_to_install_list "extras" "$file"
            if [[ "$label" == "aur" ]]; then
                AUR_ENABLED=true
            fi
        fi
        echo
    done
}

# ──────────────────────────────────────────────
# TOTALS
# ──────────────────────────────────────────────

total_package_count() {
    local total=0
    for entry in "${INSTALL_LIST[@]}"; do
        local file="${entry#*:}"
        total=$((total + $(count_packages "$file")))
    done
    echo "$total"
}

# ──────────────────────────────────────────────
# PRE-FLIGHT
# ──────────────────────────────────────────────

preflight() {
    clear
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Arch Linux Interactive Installer${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo

    if [[ ! -d /sys/firmware/efi ]]; then
        fail "System not booted in UEFI mode. This script requires UEFI."
    fi
    info "UEFI mode confirmed."

    if ! ping -c 1 archlinux.org &>/dev/null && ! ping -c 1 google.com &>/dev/null; then
        fail "No internet connection. Check your network."
    fi
    info "Internet connection confirmed."

    if [[ ! -d "$PACKAGES_DIR" ]]; then
        fail "Packages directory not found at $PACKAGES_DIR."
    fi

    if mount | grep -q " /mnt "; then
        info "Unmounting existing /mnt..."
        umount -R /mnt 2>/dev/null || true
    fi
    echo
}

# ──────────────────────────────────────────────
# PRINT PLAN
# ──────────────────────────────────────────────

print_plan() {
    echo
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Installation Plan${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo

    echo -e "  ${YELLOW}Target disk:${NC}  ${DISK}"
    echo "    ${EFI_PART}  →  1 GB EFI (vfat)"
    echo "    ${LVM_PART}  →  $([[ "$LUKS_ENCRYPT" == true ]] && echo 'LUKS → ')$(echo 'LVM → VG ArchinstallVg → LV root')"
    echo "    btrfs subvolumes: @  @home  @pkg  @log"
    echo
    echo -e "  ${YELLOW}System:${NC}"
    echo "    Hostname: ${HOSTNAME}   User: ${USERNAME}"
    echo "    Locale:   ${LOCALE}     Timezone: ${TIMEZONE}"
    echo "    Keymap:   ${KEYMAP}"
    echo "    LUKS:     $([[ "$LUKS_ENCRYPT" == true ]] && echo 'Yes' || echo 'No')"
    echo "    Desktop:  ${DESKTOP_CHOICE^}"
    echo "    Profile:  ${PROFILE^}"
    echo

    echo -e "  ${YELLOW}Auto-detected hardware:${NC}"
    echo "    CPU: ${CPU_VENDOR^}"
    echo "    GPU: ${GPU_VENDOR^}"
    [[ "$VM_TYPE" != "none" ]] && echo "    VM:  ${VM_TYPE^}"
    echo

    echo -e "  ${YELLOW}Packages by category:${NC}"
    local seen_labels=()
    for entry in "${INSTALL_LIST[@]}"; do
        local label="${entry%%:*}"
        local file="${entry#*:}"
        local count
        count=$(count_packages "$file")
        local display_name
        display_name=$(basename "$file" .txt)
        if [[ ! " ${seen_labels[*]} " =~ " ${label}:${display_name} " ]]; then
            printf "    %-25s %3d packages\n" "${display_name}" "$count"
            seen_labels+=("${label}:${display_name}")
        fi
    done
    echo "    ──────────────────────────────────"
    echo -e "    ${GREEN}Total: $(total_package_count) packages${NC}"
    echo

    echo -e "  ${YELLOW}Services enabled at boot:${NC}"
    echo -n "    "
    if [[ "$DESKTOP_CHOICE" == "gnome" ]]; then echo -n "gdm, "
    elif [[ "$DESKTOP_CHOICE" == "kde" ]]; then echo -n "sddm, "
    fi
    echo "NetworkManager, bluetooth, firewalld, cups, docker, timesyncd"
    echo

    echo -e "  ${YELLOW}Configs applied:${NC}"
    echo "    pacman.conf, mkinitcpio.conf, zram-generator.conf"
    echo "    nvidia modprobe, docker daemon, NetworkManager, dotfiles"
    echo

    echo -e "  ${RED}WARNING: ALL DATA ON ${DISK} WILL BE DESTROYED!${NC}"
    echo
    read -r -p "Proceed with installation? [Y/n] " CONFIRM
    if [[ "$CONFIRM" =~ ^[Nn] ]]; then
        fail "Installation aborted by user."
    fi
    echo
}

# ──────────────────────────────────────────────
# DISK OPERATIONS
# ──────────────────────────────────────────────

partition_disk() {
    info "Partitioning $DISK..."
    blkdiscard -f "$DISK" 2>/dev/null || true
    wipefs -af "$DISK" &>/dev/null || true

    parted -s "$DISK" mklabel gpt
    parted -s "$DISK" mkpart primary fat32 1MiB 1025MiB
    parted -s "$DISK" set 1 esp on
    parted -s "$DISK" mkpart primary 1025MiB 100%

    mkfs.fat -F32 "$EFI_PART"

    ok "Partitioned $DISK: ${EFI_PART} (EFI), ${LVM_PART} (LVM)"
}

setup_encryption() {
    if [[ "$LUKS_ENCRYPT" != true ]]; then
        return
    fi

    info "Setting up LUKS encryption on $LVM_PART..."

    local cryptdev="/dev/mapper/cryptroot"

    cryptsetup luksFormat "$LVM_PART"
    cryptsetup open "$LVM_PART" cryptroot

    LVM_PART="$cryptdev"

    ok "LUKS encryption configured."
}

setup_lvm_btrfs() {
    info "Creating LVM..."
    pvcreate -f "$LVM_PART"
    vgcreate "$VG_NAME" "$LVM_PART"
    lvcreate -l 100%FREE -n "$LV_NAME" "$VG_NAME"
    ok "LVM: VG=$VG_NAME LV=$LV_NAME"

    info "Formatting btrfs..."
    mkfs.btrfs -f "/dev/mapper/${VG_NAME}-${LV_NAME}"

    info "Creating subvolumes..."
    mount "/dev/mapper/${VG_NAME}-${LV_NAME}" /mnt
    btrfs subvolume create /mnt/@
    btrfs subvolume create /mnt/@home
    btrfs subvolume create /mnt/@pkg
    btrfs subvolume create /mnt/@log
    umount /mnt
    ok "Btrfs subvolumes created."
}

mount_all() {
    info "Mounting filesystems..."
    mount -o "${BTRFS_OPTS},subvol=/@" "/dev/mapper/${VG_NAME}-${LV_NAME}" /mnt
    mkdir -p /mnt/{home,var/cache/pacman/pkg,var/log,boot}

    mount -o "${BTRFS_OPTS},subvol=/@home" "/dev/mapper/${VG_NAME}-${LV_NAME}" /mnt/home
    mount -o "${BTRFS_OPTS},subvol=/@pkg" "/dev/mapper/${VG_NAME}-${LV_NAME}" /mnt/var/cache/pacman/pkg
    mount -o "${BTRFS_OPTS},subvol=/@log" "/dev/mapper/${VG_NAME}-${LV_NAME}" /mnt/var/log

    mount "$EFI_PART" /mnt/boot
    ok "All filesystems mounted."
}

# ──────────────────────────────────────────────
# BASE INSTALL
# ──────────────────────────────────────────────

install_base() {
    info "Installing base system..."

    local cpu_ucode=""
    if [[ "$CPU_VENDOR" == "amd" ]]; then cpu_ucode="amd-ucode"
    elif [[ "$CPU_VENDOR" == "intel" ]]; then cpu_ucode="intel-ucode"
    fi

    pacstrap -K /mnt base base-devel linux-zen linux-zen-headers \
        linux-firmware $cpu_ucode btrfs-progs lvm2 sudo vim nano \
        bash-completion git wget grub efibootmgr grub-btrfs snapper \
        cryptsetup

    ok "Base system installed."
}

generate_fstab() {
    info "Generating fstab..."
    genfstab -U /mnt > /mnt/etc/fstab
    ok "fstab generated."
}

# ──────────────────────────────────────────────
# CHROOT CONFIGURATION
# ──────────────────────────────────────────────

chroot_run() {
    arch-chroot /mnt /bin/bash -c "$1"
}

configure_system() {
    info "Configuring system..."

    chroot_run "ln -sf /usr/share/zoneinfo/${TIMEZONE} /etc/localtime"
    chroot_run "hwclock --systohc"

    chroot_run "echo '${LOCALE} UTF-8' > /etc/locale.gen"
    chroot_run "locale-gen"
    chroot_run "echo LANG=${LOCALE} > /etc/locale.conf"

    chroot_run "echo '${HOSTNAME}' > /etc/hostname"
    chroot_run "echo '127.0.1.1 ${HOSTNAME}.localdomain ${HOSTNAME}' >> /etc/hosts"
    chroot_run "echo 'KEYMAP=${KEYMAP}' > /etc/vconsole.conf"
    chroot_run "echo 'FONT=${FONT}' >> /etc/vconsole.conf"

    ok "System configured."
}

configure_initramfs() {
    info "Configuring mkinitcpio..."

    # Build hook list based on LUKS
    local hooks="base udev autodetect microcode modconf kms keyboard keymap consolefont"

    if [[ "$LUKS_ENCRYPT" == true ]]; then
        hooks="$hooks block encrypt lvm2 filesystems fsck"
    else
        hooks="$hooks block lvm2 filesystems fsck"
    fi

    cat > /mnt/etc/mkinitcpio.conf <<- MKINIT
MODULES=()
BINARIES=()
FILES=()
HOOKS=($hooks)
COMPRESSION="zstd"
MKINIT

    chroot_run "mkinitcpio -P"
    ok "Initramfs rebuilt."
}

install_grub() {
    info "Installing GRUB..."

    local cryptdisk="n"
    local cmdline="loglevel=3 quiet"

    if [[ "$LUKS_ENCRYPT" == true ]]; then
        cryptdisk="y"
        cmdline="$cmdline cryptdevice=${LVM_PART}:cryptroot root=/dev/mapper/${VG_NAME}-${LV_NAME}"
    fi

    # Write GRUB config directly (not in chroot, to avoid quoting issues)
    cat > /mnt/etc/default/grub << GRUB
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="Arch"
GRUB_CMDLINE_LINUX_DEFAULT="${cmdline}"
GRUB_CMDLINE_LINUX=""
GRUB_PRELOAD_MODULES="part_gpt part_msdos"
GRUB_TIMEOUT_STYLE=menu
GRUB_TERMINAL_INPUT=console
GRUB_GFXMODE=auto
GRUB_GFXPAYLOAD_LINUX=keep
GRUB_DISABLE_RECOVERY=true
GRUB_ENABLE_CRYPTODISK=${cryptdisk}
GRUB

    chroot_run "grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Arch"
    chroot_run "grub-mkconfig -o /boot/grub/grub.cfg"
    ok "GRUB installed."
}

# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

setup_users() {
    echo
    info "Setting up root password..."
    chroot_run "passwd"

    echo
    info "Creating user '${USERNAME}'..."
    chroot_run "useradd -m -G wheel -s /bin/bash ${USERNAME}"
    info "Password for '${USERNAME}':"
    chroot_run "passwd ${USERNAME}"
    chroot_run "sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers"
    ok "User '${USERNAME}' created with sudo."
}

# ──────────────────────────────────────────────
# PACKAGE INSTALLATION
# ──────────────────────────────────────────────

install_packages() {
    local file="$1"
    local label="$2"

    if [[ ! -f "$file" ]]; then
        return
    fi

    local packages
    packages=$(read_packages "$file" | tr '\n' ' ')
    if [[ -z "$packages" ]]; then
        return
    fi

    info "Installing ${label}..."
    chroot_run "pacman -S --noconfirm --needed --ask 4 $packages"
    ok "${label} installed."
}

install_all_packages() {
    info "Installing packages..."

    for entry in "${INSTALL_LIST[@]}"; do
        local file="${entry#*:}"
        local label
        label=$(basename "$file" .txt)

        # Skip AUR packages (handled by install_aur)
        [[ "$label" == "aur" ]] && continue

        install_packages "$file" "$label"
    done

    ok "All repository packages installed."
}

install_aur() {
    if [[ "$AUR_ENABLED" != true ]]; then
        return
    fi

    info "Installing yay AUR helper..."
    chroot_run "pacman -S --noconfirm --needed --ask 4 go"
    chroot_run "cd /tmp && git clone https://aur.archlinux.org/yay.git && chown -R ${USERNAME} yay"
    chroot_run "cd /tmp/yay && sudo -u ${USERNAME} makepkg -si --noconfirm"

    info "Installing AUR packages..."
    local aur_packages
    aur_packages=$(read_packages "$PACKAGES_DIR/aur.txt" | tr '\n' ' ')
    if [[ -n "$aur_packages" ]]; then
        chroot_run "sudo -u ${USERNAME} yay -S --noconfirm $aur_packages"
    fi
    ok "AUR packages installed."
}

# ──────────────────────────────────────────────
# CONFIGS & DOTFILES
# ──────────────────────────────────────────────

copy_configs() {
    info "Copying system configs..."
    cp "$CONFIGS_DIR/pacman.conf" /mnt/etc/pacman.conf
    cp "$CONFIGS_DIR/zram-generator.conf" /mnt/etc/systemd/zram-generator.conf

    mkdir -p /mnt/etc/modprobe.d
    if [[ "$GPU_VENDOR" == "nvidia" ]] && [[ -f "$CONFIGS_DIR/modprobe.d/nvidia.conf" ]]; then
        cp "$CONFIGS_DIR/modprobe.d/nvidia.conf" /mnt/etc/modprobe.d/nvidia.conf
    fi

    mkdir -p /mnt/etc/docker
    if [[ "$GPU_VENDOR" == "nvidia" ]] && [[ -f "$CONFIGS_DIR/docker/daemon.json" ]]; then
        cp "$CONFIGS_DIR/docker/daemon.json" /mnt/etc/docker/daemon.json
    fi

    mkdir -p /mnt/etc/NetworkManager/conf.d
    cp "$CONFIGS_DIR/NetworkManager/conf.d/00-config.conf" /mnt/etc/NetworkManager/conf.d/00-config.conf
    ok "System configs copied."
}

copy_dotfiles() {
    info "Copying user dotfiles..."
    chroot_run "mkdir -p /home/${USERNAME}"

    cp "$DOTFILES_DIR/bashrc" "/mnt/home/${USERNAME}/.bashrc"
    cp "$DOTFILES_DIR/bash_profile" "/mnt/home/${USERNAME}/.bash_profile"
    cp "$DOTFILES_DIR/gitconfig" "/mnt/home/${USERNAME}/.gitconfig"

    chroot_run "chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}"
    ok "Dotfiles copied."
}

# ──────────────────────────────────────────────
# SERVICES
# ──────────────────────────────────────────────

enable_services() {
    info "Enabling services..."

    # Display manager
    if [[ "$DESKTOP_CHOICE" == "gnome" ]]; then
        chroot_run "systemctl enable gdm.service"
    elif [[ "$DESKTOP_CHOICE" == "kde" ]]; then
        chroot_run "systemctl enable sddm.service"
    fi

    # Core services
    chroot_run "systemctl enable NetworkManager.service"
    chroot_run "systemctl enable bluetooth.service"
    chroot_run "systemctl enable systemd-timesyncd.service"
    chroot_run "systemctl enable firewalld.service"

    # Extras (conditional on being in install list)
    local all_extras=""
    for entry in "${INSTALL_LIST[@]}"; do
        all_extras="$all_extras ${entry#*:}"
    done

    if echo "$all_extras" | grep -q "printing.txt"; then
        chroot_run "systemctl enable cups.service"
    fi

    if echo "$all_extras" | grep -q "development.txt"; then
        chroot_run "systemctl enable docker.service"
    fi

    ok "All services enabled."
}

# ──────────────────────────────────────────────
# FINISH
# ──────────────────────────────────────────────

print_done() {
    echo
    echo -e "${GREEN}══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════${NC}"
    echo
    echo "  Hostname:  ${HOSTNAME}"
    echo "  User:      ${USERNAME}"
    echo "  Disk:      ${DISK}"
    echo "  Desktop:   ${DESKTOP_CHOICE^}"
    echo "  GPU:       ${GPU_VENDOR^}"
    echo "  LUKS:      $([[ "$LUKS_ENCRYPT" == true ]] && echo 'Yes' || echo 'No')"
    echo
    echo "  Next steps:"
    echo "    1. umount -R /mnt"
    echo "    2. reboot"
    echo "    3. Log in as ${USERNAME}"
    echo "    4. Authenticate: gh auth login"
    echo
}

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

main() {
    preflight
    detect_hardware
    select_disk
    prompt_config
    build_install_list
    print_plan

    partition_disk
    setup_encryption
    setup_lvm_btrfs
    mount_all
    install_base
    generate_fstab
    configure_system
    configure_initramfs
    install_grub
    setup_users
    install_all_packages
    copy_configs
    enable_services
    copy_dotfiles
    install_aur

    print_done
}

main
