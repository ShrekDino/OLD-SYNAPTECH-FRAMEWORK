#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# Part 1: Install built AUR packages via pkexec
# ──────────────────────────────────────────────
echo "Step 1/4: Installing AUR packages (GUI password prompt will appear)..."

pkexec pacman -U --noconfirm \
  /home/cinni/.cache/yay/signal-cli/signal-cli-0.14.4.1-1-any.pkg.tar.zst \
  /home/cinni/.cache/yay/pamac-aur/pamac-aur-11.7.5-1-x86_64.pkg.tar.zst \
  /home/cinni/.cache/yay/appimagelauncher/appimagelauncher-3.0.0_beta_3-1-x86_64.pkg.tar.zst \
  /home/cinni/.cache/yay/appimagelauncher/appimagelauncher-debug-3.0.0_beta_3-1-x86_64.pkg.tar.zst \
  /home/cinni/.cache/yay/miniconda3/miniconda3-26.3.2.2-1-x86_64.pkg.tar.zst

echo "  AUR packages installed."

# ──────────────────────────────────────────────
# Part 2: Remove broken .local/bin/env lines
# ──────────────────────────────────────────────
echo "Step 2/4: Fixing bash config..."

# Remove the broken source line from .bashrc
sed -i '/^\. "\$HOME\/\.local\/bin\/env"$/d' /home/cinni/.bashrc
# Remove the broken source line from .bash_profile
sed -i '/^\. "\$HOME\/\.local\/bin\/env"$/d' /home/cinni/.bash_profile

echo "  Removed . \"\$HOME/.local/bin/env\" from bash config."

# ──────────────────────────────────────────────
# Part 3: Initialize conda
# ──────────────────────────────────────────────
echo "Step 3/4: Initializing conda..."

export PATH="/opt/miniconda3/bin:$PATH"
conda init bash

echo "  Conda initialized."

# ──────────────────────────────────────────────
# Part 4: Verify
# ──────────────────────────────────────────────
echo "Step 4/4: Verification..."

echo "  Packages installed:"
pacman -Q pamac-aur signal-cli appimagelauncher miniconda3 2>&1

echo ""
echo "  Conda version:"
conda --version 2>/dev/null || echo "  conda not found in PATH yet (will work after new terminal)"

echo ""
echo "✅ Setup complete! Close and reopen your terminal to verify the error is gone."
