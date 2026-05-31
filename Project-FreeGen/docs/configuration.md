# Configuration

FreeGen supports three levels of configuration (precedence: CLI > Profile > Config File > Defaults).

## CLI Arguments

```bash
freegen [options]

Options:
  --version                 Print version and exit
  -c,--config PATH          Path to custom config file
  -p,--profile NAME         Profile name to use
  --capture-source SOURCE   Capture source (monitor, window, etc.)
  --upscaler NAME           Upscaler (Off, FSR 1.0, Integer, ...)
  --frame-gen MODE          Frame generation mode (Off, Interpolate)
  --sharpness VALUE         Sharpness (0.0-2.0)
  --scale VALUE             Scale factor (1-6)
  --no-vsync                Disable vsync
  --no-overlay              Hide overlay UI
  --list-sources            List available capture sources
  --list-effects            List available effects
  --width W                 Output width
  --height H                Output height
  --fps N                   Target FPS
```

## Config File

Location: `~/.config/freegen/config.json`

```json
{
    "capture_mode": "auto",
    "capture_source": "",
    "upscaler": "FSR 1.0",
    "frame_gen": "Off",
    "sharpness": 0.5,
    "scale_factor": 2.0,
    "vsync": true,
    "show_fps": true,
    "show_overlay": true,
    "max_fps": 0,
    "active_profile": "Default"
}
```

## Profiles

Profiles allow per-game/per-application configurations stored in `~/.config/freegen/profiles/<name>.json`:

```json
{
    "upscaler": "Integer",
    "frame_gen": "Interpolate",
    "sharpness": 0.0,
    "scale_factor": 3.0,
    "vsync": false
}
```

Auto-detection maps running process names to profiles:
- `steam*` → "Steam Game"
- `gamescope` → "Gamescope Session"
- `wine*` / `proton` → "Wine/Proton Game"

## Default Values

| Setting | Default | Description |
|---------|---------|-------------|
| capture_mode | auto | Capture mode (auto/desktop/window) |
| upscaler | Off | Active upscaler |
| frame_gen | Off | Frame generation mode |
| sharpness | 0.5 | Sharpening strength |
| scale_factor | 2.0 | Output scale multiplier |
| vsync | true | V-sync enabled |
| show_fps | true | FPS counter visible |
| show_overlay | true | Settings overlay visible |
| max_fps | 0 | FPS limit (0 = unlimited) |
