#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

echo "=== Ruffel Mono Agent Bootstrap ==="
echo ""

# Step 1: Build OpenMono.Cli
echo "[1/5] Building OpenMono.Cli..."
dotnet build "$REPO_ROOT/OpenMono.sln" -c Release 2>&1 | tail -3

OPENMONO_BIN="$REPO_ROOT/src/OpenMono.Cli/bin/Release/net10.0/openmono"
if [ ! -f "$OPENMONO_BIN" ]; then
  OPENMONO_BIN="$REPO_ROOT/src/OpenMono.Cli/bin/Release/net10.0/openmono.dll"
  if [ ! -f "$OPENMONO_BIN" ]; then
    echo "ERROR: openmono binary not found after build."
    exit 1
  fi
  echo "  -> Built DLL: $OPENMONO_BIN"
else
  echo "  -> Built: $OPENMONO_BIN"
fi

# Step 2: Build the VS Code Extension
echo ""
echo "[2/5] Building VS Code extension..."

EXTENSION_DIR="$REPO_ROOT/opencode/sdks/vscode"
cd "$EXTENSION_DIR"

if command -v bun &> /dev/null; then
  echo "  Using bun..."
  bun install 2>&1 | tail -1
  bun run compile 2>&1
elif command -v npm &> /dev/null; then
  echo "  Using npm..."
  npm install 2>&1 | tail -3
  npm run compile 2>&1
else
  echo "ERROR: bun or npm required for building the VS Code extension"
  exit 1
fi

cd "$REPO_ROOT"
echo "  -> Extension built at $EXTENSION_DIR/dist/extension.js"

# Step 3: Symlink the binary into the extension
echo ""
echo "[3/5] Linking openmono binary..."

OPENMONO_EXE="openmono"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  OPENMONO_EXE="openmono.exe"
fi

SYMLINK_DIR="$EXTENSION_DIR/bin"
mkdir -p "$SYMLINK_DIR"

# Remove old symlink if exists
if [ -L "$SYMLINK_DIR/$OPENMONO_EXE" ]; then
  rm "$SYMLINK_DIR/$OPENMONO_EXE"
fi

ln -sf "$OPENMONO_BIN" "$SYMLINK_DIR/$OPENMONO_EXE"
echo "  -> Symlink: $SYMLINK_DIR/$OPENMONO_EXE"
chmod +x "$SYMLINK_DIR/$OPENMONO_EXE" 2>/dev/null || true

# Step 4: Create workspace VSCode settings
echo ""
echo "[4/5] Writing workspace configuration..."

WORKSPACE_SETTINGS="$REPO_ROOT/.vscode/settings.json"
mkdir -p "$(dirname "$WORKSPACE_SETTINGS")"

cat > "$WORKSPACE_SETTINGS" << 'SETTINGS'
{
  "ruffelMonoAgent.binaryPath": "${workspaceFolder}/opencode/sdks/vscode/bin/openmono",
  "ruffelMonoAgent.localEndpoint": "http://localhost:7474",
  "ruffelMonoAgent.dataDir": "${userHome}/.openmono",
  "ruffelMonoAgent.renderer": "vscode"
}
SETTINGS
echo "  -> Settings written to $WORKSPACE_SETTINGS"

# Step 5: Create OpenMono user settings if not present
echo ""
echo "[5/5] Creating OpenMono user config..."

OPENMONO_USER_DIR="${HOME}/.openmono"
OPENMONO_USER_CONFIG="${OPENMONO_USER_DIR}/settings.json"

if [ ! -f "$OPENMONO_USER_CONFIG" ]; then
  mkdir -p "$OPENMONO_USER_DIR"
  cat > "$OPENMONO_USER_CONFIG" << 'CONFIG'
{
  "llm": {
    "endpoint": "http://localhost:7474",
    "model": ""
  },
  "renderer": "vscode"
}
CONFIG
  echo "  -> Created: $OPENMONO_USER_CONFIG"
  echo "  -> Edit this file to set your LLM endpoint and model."
else
  echo "  -> Config exists: $OPENMONO_USER_CONFIG (skipped)"
fi

echo ""
echo "============================================"
echo "  Ruffel Mono Agent Bootstrap Complete!"
echo "============================================"
echo ""
echo "Quick start:"
echo "  1. Make sure your LLM server is running:"
echo "     curl http://localhost:7474/health"
echo ""
echo "  2. Open this workspace in VS Code:"
echo "     code $REPO_ROOT"
echo ""
echo "  3. Press Cmd+Esc to open the Agent Chat panel"
echo "     or click the robot icon in the activity bar."
echo ""
echo "  4. The agent will start automatically."
echo ""
echo "To rebuild the dotnet backend:"
echo "  dotnet build $REPO_ROOT/OpenMono.sln -c Release"
echo ""
echo "To rebuild the extension:"
echo "  cd $EXTENSION_DIR && npm run compile"
echo ""
