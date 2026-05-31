# Packaging

FreeGen supports multiple packaging formats for distribution.

## Flatpak

```bash
# Build
./scripts/build-flatpak.sh

# Install
flatpak install freegen.flatpak

# Run
flatpak run io.github.freegen
```

The Flatpak manifest is at `flatpak/io.github.freegen.yml` with:
- X11/Wayland socket access
- DRI device access (GPU)
- PipeWire socket access
- XDG Desktop Portal access for screen capture

## AppImage

```bash
# Build (requires appimagetool)
./scripts/build-appimage.sh

# Run
./freegen-x86_64.AppImage
```

Requirements for AppImage runtime:
- FUSE 2.x or 3.x
- Vulkan runtime libraries

## Docker

```bash
# Development container
docker compose run --rm dev

# Build-only container
docker compose up build

# Production image
docker build --target runtime -t freegen:latest .
docker run --rm -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --device /dev/dri \
    --group-add video \
    freegen:latest
```

## Build from Source

See the [Build Guide](build.md) for detailed build instructions for all platforms.
