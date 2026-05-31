# SamChat — Silent by Default, Urgent by Intent

A decentralized messaging app built on the **Matrix Protocol** with a notification gate: all rooms start muted, only tagged-urgent messages break through.

---

## Philosophy

Most chat apps blast every notification. SamChat flips it: **quiet is the default, urgency is opt-in**. A user long-pressing send to mark a message as urgent means it genuinely matters — and the UI/notification system treats it that way (crimson border, siren icon, high-importance push). Everything else waits silently.

---

## Architecture

| Layer | Choice |
|---|---|
| Framework | Flutter 3.44 / Dart 3.x |
| Matrix SDK | Famedly `matrix: ^0.27.0` |
| State | Riverpod 2.x (StateNotifier + StreamProvider + FutureProvider) |
| Routing | go_router 14.x (auth guards, deep links) |
| Session | SharedPreferences (token + userID + deviceID) |
| Notifications | flutter_local_notifications (2 channels: HIGH / LOW) + Firebase Cloud Messaging |
| Sending | Raw HTTP to Matrix CS API (bypasses SDK for custom `org.custom.urgency` field) |
| Event listening | `client.onEvent` stream for incoming timeline events |

---

## Directory Layout

```
lib/
├── main.dart                  # Entry point
├── app.dart                   # MaterialApp.router
├── core/
│   ├── design/                # Colors, ThemeData
│   ├── matrix/                # Auth service, Push rule service, Event extensions
│   ├── models/                # NotificationPriority, DeviceIdentity, Telemetry
│   ├── services/              # SharedPreferences provider, Connectivity, Crash reporter, GitHub, Telemetry
│   └── router.dart            # go_router config
├── ui/
│   ├── providers/             # Riverpod providers (activeRoomId)
│   ├── layouts/               # Responsive scaffold, panels
│   └── views/                 # Login screen, chat bubble groups
├── features/
│   ├── auth/                  # AuthNotifier
│   ├── chat/                  # Timeline, input bar, message bubbles
│   ├── notifications/         # Dual-channel local notifications, push gateway
│   ├── rooms/                 # Room list, DM/Group/Join creation, user search
│   ├── settings/              # Full settings system (5 sections, 12 controls)
│   └── stickers/              # MSC2545 image pack picker
├── shared/widgets/            # Urgent indicator, info dialog
├── scripts/                   # Build & release automation scripts
├── CHANGELOG.md               # Release history
└── .github/workflows/         # CI/CD pipeline
```

---

## Current State (v0.6.2)

### Working
- Matrix login (homeserver URL + MXID + password, or OIDC/SSO)
- **Homeserver picker**: Scrollable list of 6 pre-configured servers + custom URL expandable card
- **Probe-based flow**: Detects server auth support (password/SSO) and shows appropriate form
- Session persistence (SharedPrefs restore on cold start)
- Push rule `.org.custom.urgency` auto-setup after login
- Background sync via SDK
- Room list (sorted by last event, unread badges, timestamps)
- New DM (user directory search) + New Group + Join Room
- Chat screen: **send AND receive messages** (timeline wired to `client.onEvent`)
- **Read markers** sent on entering a chat room
- **Logout** via AppBar popup menu
- Silent/Urgent toggle (long-press send button, pulse animation, haptics)
- MSC2545 sticker picker keyboard
- Dual-channel local notifications (HIGH for urgent, LOW for silent)
- OLED-dark theme
- **Network-resilient auth**: SocketException handling, `disconnected` state, `retryConnection()`, login + session timeout
- **Bug reporting**: Global FlutterError handler + Connectivity queue → GitHub Issues (`samchat-reports`)
- **Telemetry**: 5min heartbeat + 12h digest of sync health, message delivery, login events
- **Responsive layout**: 3-column desktop, 2-column tablet, 1-column mobile
- **Collapsible NavigationRail**: Animated icon-only / labeled toggle
- **Clustered message groups**: Same-sender within 5 min chained under single avatar header
- **Connected bubble radii**: Adjusted corner radii per position (first/middle/last) in group
- **Material icons fix**: `--no-tree-shake-icons` + `cupertino_icons`
- **Settings screen**: Full settings page with Appearance, Notifications, Privacy, Chat, About sections
- **Dynamic accent colors**: 8 color options (blue, crimson, purple, green, orange, yellow, teal, pink)
- **Theme modes**: Dark/Light/System with persistent selection
- **Bubble style picker**: Modern/Rounded/Compact bubble corner options
- **Notification toggles**: Urgent sound + silent vibration
- **Privacy toggles**: Read receipts + typing indicators
- **Chat settings**: Font size slider + enter-to-send toggle
- **Open source licenses**: Built-in license viewer
- **Timeline pagination**: `requestHistory()` loaded when entering room, infinite scroll-up pagination
- **SamiCodex**: Developer preferences and coding philosophies codex (`.opencode/samicodex.md`)
- **Multi-platform build scripts**: Android (APK/AAB), Linux, Windows, macOS build and release scripts
- **CI/CD pipeline**: Automated GitHub Actions workflow on tag-push and PR quality check
- **Firebase Cloud Messaging (FCM)**: Push notification transport wired via foreground + background handlers, routing urgent/silent messages to `PushGateway`
- Build succeeds

### Missing
- No encryption handling
- No reactions / edits / replies
- Error handling is inconsistent
- No real tests

---

## Key Design Decisions

| Decision | Why |
|---|---|
| **Raw HTTP for sending** (not SDK `sendEvent`) | Need to inject `org.custom.urgency` in event content; SDK doesn't support custom fields |
| **`client.onEvent` for receiving** (not `room.onUpdate`) | onEvent fires for every timeline event with full JSON; room.onUpdate is less granular |
| **AuthNotifier owns the Client** (not a separate provider) | Single source of truth; avoids stale client references |
| **SharedPreferences for session** (not SDK database) | Simpler, no migrations needed |
| **Separate notification channels** | Android requires different importance per channel; cleanly separates urgent from silent |
| **Every commit = new GitHub release** | Active maintenance signal; APK always available |

---

## Build

### Prerequisites

```bash
# Flutter 3.44+
git clone -b stable https://github.com/flutter/flutter.git ~/flutter

# Android SDK 36 (for Android builds)
sdkmanager "platforms;android-36" "build-tools;36.0.0" "ndk;28.2.13676358"

# JDK 21
flutter config --jdk-dir ~/jdk21

# Linux desktop (if building for Linux)
sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev libjsoncpp-dev libwebkit2gtk-4.1-dev
```

### Build Commands

```bash
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

```bash
GITHUB_PAT=ghp_xxx flutter build apk --release --no-tree-shake-icons \
  --dart-define=GITHUB_PAT=$GITHUB_PAT
```

Flutter 3.44 · JDK 21 · Android SDK 36 · NDK 28.2.13676358  
Keystore: `android/app/samchat-keystore.jks` (RSA 2048)  
`applicationId`: `com.samchat.app`
