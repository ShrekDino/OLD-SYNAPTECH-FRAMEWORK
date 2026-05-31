# SamChat — Silent by Default, Urgent by Intent

[![CI](https://github.com/anomalyco/samchat/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/samchat/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/anomalyco/samchat?style=flat-square&logo=github)](https://github.com/anomalyco/samchat/releases)
[![License](https://img.shields.io/github/license/anomalyco/samchat?style=flat-square)](LICENSE)
[![Flutter](https://img.shields.io/badge/Flutter-3.44-blue?style=flat-square&logo=flutter)](https://flutter.dev)

A decentralized messaging app built on the **Matrix Protocol** with a notification gate: messages are **silent by default**, only tagged-urgent breaks through.

> Quiet is the default. Urgency is intent.

---

## Download

| Platform | Download | Requirements |
|----------|----------|-------------|
| Android | [APK (universal)](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2-universal.apk) · [APK (arm64)](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2-arm64-v8a.apk) · [AAB](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2.aab) | Android 5.0+ (API 21) |
| Linux | [tar.gz](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2-linux-x86_64.tar.gz) | GTK 3, x86_64 |
| Windows | [zip](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2-win64.zip) | Windows 10+ |
| macOS | [DMG](https://github.com/anomalyco/samchat/releases/latest/download/SamChat-v0.6.2-macos.dmg) | macOS 10.15+ |

All releases include SHA256 checksums. See the [Releases page](https://github.com/anomalyco/samchat/releases) for the full history.

---

## Features

- **Silent/Urgent toggle** — long-press send to mark a message urgent (crimson border, siren icon, high-importance push notification)
- **Matrix protocol** — fully compatible with Element, FluffyChat, Nheko, and any Matrix client
- **Firebase Cloud Messaging** — FCM push notifications wired for urgent (high priority) and silent (tray-only) delivery
- **End-to-end encryption ready** — SDK integrated, encryption support planned
- **Sticker picker** — MSC2545 image pack support
- **Push notifications** — dual-channel (HIGH urgent / LOW silent) via `flutter_local_notifications`
- **Responsive UI** — 3-column desktop, 2-column tablet, 1-column mobile, all adaptive
- **Customizable** — 8 accent colors, dark/light/system themes, 3 bubble styles, font size slider
- **OLED dark theme** — pure black backgrounds, battery-friendly on OLED screens
- **Message grouping** — same-sender messages within 5 minutes grouped under a single avatar
- **Timeline pagination** — infinite scroll loads historical messages from any Matrix client
- **Session persistence** — stays logged in across restarts
- **OIDC/SSO login** — supports password and single sign-on
- **Network resilient** — graceful disconnect handling with retry
- **Settings** — Appearance, Notifications, Privacy, Chat, About with Open Source licenses
- **Automatic bug reporting** — crashes captured and queued to GitHub Issues

---

## Building from Source

### Prerequisites

```bash
# Flutter 3.44+
git clone -b stable https://github.com/flutter/flutter.git ~/flutter

# Android SDK 36 (for Android builds)
sdkmanager "platforms;android-36" "build-tools;36.0.0" "ndk;28.2.13676358"

# JDK 21
flutter config --jdk-dir ~/jdk21
```

### Build Commands

```bash
# Install dependencies
flutter pub get

# Android — universal APK
flutter build apk --release --no-tree-shake-icons

# Android — per-architecture (smaller APKs)
flutter build apk --release --split-per-abi --no-tree-shake-icons

# Android — App Bundle (Play Store)
flutter build appbundle --release

# Linux
flutter build linux --release

# Windows
flutter build windows --release

# macOS
flutter build macos --release
```

### Automation Scripts

```bash
# Build a specific platform
./scripts/build-android.sh   # APK (universal + per-abi) + AAB
./scripts/build-linux.sh     # Linux tarball
./scripts/build-windows.sh   # Windows zip
./scripts/build-macos.sh     # macOS DMG

# Full release pipeline (version bump → build → tag → release)
./scripts/release.sh
```

### Firebase Push Notifications

FCM is wired in the app but requires credential files to function:

1. Place `google-services.json` in `android/app/` (from Firebase Console)
2. Place `GoogleService-Info.plist` in `ios/Runner/` (from Firebase Console)
3. Build and run — push notifications work automatically

These files contain sensitive credentials and must not be committed.

### Crash Reporting

Pass a GitHub Personal Access Token to enable automatic crash reporting:

```bash
GITHUB_PAT=ghp_xxx flutter build apk --release --no-tree-shake-icons \
  --dart-define=GITHUB_PAT=$GITHUB_PAT
```

---

## Architecture

```
lib/
├── main.dart                   # Entry point
├── app.dart                    # MaterialApp.router with OLED-dark theme
├── core/
│   ├── design/                 # Colors, ThemeData
│   ├── matrix/                 # Auth service, Push rules, Event extensions
│   ├── models/                 # NotificationPriority, DeviceIdentity, Telemetry
│   ├── services/               # Connectivity, Crash reporter, GitHub, Telemetry
│   └── router.dart             # go_router config with auth guards
├── features/
│   ├── auth/                   # AuthNotifier (Riverpod): login, restore, OIDC, logout
│   ├── chat/                   # Chat model, state, notifier, input bar, message groups
│   ├── notifications/          # Dual-channel notifications, push gateway
│   ├── rooms/                  # Room list, DM/Group creation, user search
│   ├── settings/               # Full settings system (5 sections, 12 controls)
│   └── stickers/               # MSC2545 image pack picker
├── ui/
│   ├── layouts/                # Responsive scaffold (3/2/1 columns), panels
│   ├── providers/              # Active room state
│   └── views/                  # Homeserver picker, chat bubble groups
└── shared/widgets/             # Urgent indicator, info dialog
```

**State Management:** Riverpod (StateNotifier + StreamProvider + FutureProvider)
**Routing:** go_router with auth guards and deep links
**Matrix SDK:** `matrix: ^0.27.0` (Famedly)
**Notifications:** `flutter_local_notifications` (2 channels: HIGH / LOW)

---

## How Urgent Works

1. **Send:** Long-press the send button → toggles urgent mode (pulse animation, crimson color)
2. **Flag:** Message is sent with `org.custom.urgency: "urgent"` in the Matrix event content
3. **Server:** A push rule matches this field and overrides default mute behavior
4. **Receive:** Recipient sees a crimson border, siren icon, and gets a high-importance notification
5. **Default:** Without the flag, messages are silent — no sound, no vibration, tray-only

---

## Project Status

See [CHANGELOG.md](CHANGELOG.md) for release history and [AGENTS.md](AGENTS.md) for detailed project state.

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
