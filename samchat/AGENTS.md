# SamChat — Agent Handoff

Execution-critical details only. For project overview / philosophy see `PROJECT.md`.

---

## File Map

```
lib/
├── main.dart                          # Entry point: Firebase init, FCM listeners, notifications, SharedPreferences, run app
├── app.dart                           # MaterialApp.router with OLED-dark theme
│
├── core/
│   ├── design/
│   │   ├── app_colors.dart            # Color palette (OLED #000000 bg, accent crimson/silent)
│   │   └── app_theme.dart             # Light/dark ThemeData
│   ├── matrix/
│   │   ├── auth_service.dart          # Login/session persistence via Matrix SDK + SharedPrefs
│   │   ├── push_rule_service.dart     # CRUD for org.custom.urgency override push rule
│   │   └── event_extensions.dart      # Extensions on Matrix Event objects
│   ├── models/
│   │   ├── notification_priority.dart # Enum: silent / urgent, toggle() logic
│   │   ├── device_identity.dart       # Device ID tracking for session restore
│   │   └── telemetry_report.dart      # Telemetry event data models
│   ├── services/
│   │   ├── shared_preferences_provider.dart # Provider<SharedPreferences> — overridden in main()
│   │   ├── connectivity_queue.dart    # Offline buffer for crash/telemetry reports
│   │   ├── crash_reporter.dart        # Global error handler, queues reports
│   │   ├── github_config.dart         # PAT config for GitHub Issues
│   │   ├── github_issue_service.dart  # Creates GitHub Issues for crash reports
│   │   └── telemetry_service.dart     # 5min heartbeat + 12h digest telemetry
│   └── router.dart                    # go_router config with auth guards
│
├── ui/
│   ├── providers/
│   │   └── active_room_provider.dart  # StateProvider<String?> for selected room in split-view
│   ├── layouts/
│   │   ├── responsive_scaffold.dart   # 3-column (desktop) / 2-column (tablet) / 1-column (mobile)
│   │   ├── room_list_panel.dart       # Reusable room list body with loading/error/data states
│   │   └── chat_panel.dart            # Reusable chat timeline + input bar with pagination
│   └── views/
│       ├── login/
│       │   └── homeserver_picker_view.dart  # FluffyChat-inspired server list + password/SSO forms
│       └── chat/
│           └── widgets/
│               └── chat_bubble_group.dart   # Clustered message groups + urgency markers
│
├── features/
│   ├── auth/
│   │   └── state/
│   │       └── auth_notifier.dart     # AuthNotifier (Riverpod): restore, login, OIDC, logout, error, retry, sync status
│   ├── chat/
│   │   ├── models/
│   │   │   └── chat_message.dart      # ChatMessage data class with urgency, copyWith
│   │   ├── state/
│   │   │   ├── chat_state.dart        # Composing text, priority, messages, sticker packs, pagination state
│   │   │   └── chat_notifier.dart     # Send via raw HTTP (uses Matrix CS API directly)
│   │   │                              # Also listens to Client.onEvent for incoming + history messages
│   │   └── widgets/
│   │       ├── chat_input_bar.dart    # Text field + urgent long-press + send button
│   │       └── chat_screen.dart       # Thin Scaffold wrapper around ChatPanel
│   ├── notifications/
│   │   ├── notification_channels.dart # HIGH urgent + LOW silent channel init
│   │   ├── notification_service.dart  # Singleton: showUrgent, showSilent, showInsistentUrgent
│   │   └── push_gateway.dart         # Push payload parser + FCM handler with urgency routing
│   ├── rooms/
│   │   ├── providers/
│   │   │   └── room_list_provider.dart # StreamProvider from client.onSync, sorted by lastEvent
│   │   ├── services/
│   │   │   └── room_service.dart      # startDirectChat, createGroup, joinRoom, searchUsers
│   │   └── widgets/
│   │       ├── room_list_screen.dart  # Thin Scaffold wrapper around RoomListPanel
│   │       ├── room_tile.dart         # Avatar (deterministic color), 3-line, unread badge, time
│   │       ├── new_chat_fab.dart      # Speed-dial bottom sheet: New DM, Group, Join
│   │       ├── create_group_sheet.dart# Group name input + create
│   │       ├── join_room_sheet.dart   # Room alias/ID input + join
│   │       └── user_search_delegate.dart # Search delegate for Matrix user directory
│   └── stickers/
│       ├── models/
│       │   ├── sticker_pack.dart      # MatrixImagePack, MatrixSticker, ImagePackStatus
│       │   └── sticker_message.dart   # StickerMessageContent with urgency field
│       ├── services/
│       │   └── sticker_service.dart   # getPacks via CS API _matrix/client/v3/rooms/...
│       └── widgets/
│           └── sticker_picker_keyboard.dart # Grid picker, loads from room state
│
├── settings/                          # Handled via go_router `/settings` route
│   └── lib/features/settings/         # Full settings widget tree in features/
│
└── shared/
    └── widgets/
        ├── urgent_indicator.dart      # Siren glyph widget
        └── urgent_info_dialog.dart    # "What is urgent?" explanation dialog

platform/                              # Desktop/mobile platform scaffolding
├── android/                           # Android project (compileSdk=36, NDK 28)
├── ios/                               # iOS project (Xcode, Swift)
├── linux/                             # Linux project (GTK3, CMake)
├── macos/                             # macOS project (Xcode, Swift)
└── windows/                           # Windows project (C++)

scripts/                               # Build & release automation
├── release.sh                         # Master release script: version bump → build → tag → GitHub Release
├── build-android.sh                   # Android APK (universal + per-abi) + AAB
├── build-linux.sh                     # Linux tarball
├── build-windows.sh                   # Windows portable zip
├── build-macos.sh                     # macOS DMG
└── update-version.sh                  # Version string bump in pubspec + source files

.github/
└── workflows/
    ├── ci.yml                         # Quality gate: flutter analyze + flutter test on push/PR
    └── release.yml                    # Automated multi-platform build + GitHub Release on tag push
```

---

## Critical SDK API Shapes (matrix: ^0.27.0)

These **differ from common assumptions**. Get these wrong → build fails.

### Login
```dart
final client = Client('SamChat');
await client.checkHomeserver(Uri.parse(homeserver));
await client.login(
  LoginType.mLoginPassword,
  identifier: AuthenticationUserIdentifier(user: username),
  password: password,
  initialDeviceDisplayName: 'SamChat',
);
```

### Session Restore
```dart
final client = Client('SamChat');
await client.checkHomeserver(Uri.parse(session.homeserver));
await client.init(
  newToken: session.accessToken,
  newUserID: session.userId,
  newDeviceID: session.deviceId,
  newDeviceName: 'SamChat',
  newHomeserver: Uri.parse(session.homeserver),
  waitForFirstSync: false,
);
```
Save `deviceID` alongside accessToken/userId for restore.

### Sync
`client.backgroundSync = true` — not `startSyncing()`.
Background sync defaults to `true` in the SDK but we set it explicitly.

### Room API
- `room.notificationCount` (int) — not `unreadCount`
- `room.highlightCount` (int)
- `room.isDirectChat` (bool get) — not `isDirect`
- `room.getLocalizedDisplayname()` — no parameters
- `room.name` is `String` (empty if unset), not `String?`
- `room.lastEvent` is `Event?` (SDK wrapper, not the generated model)
- `room.setReadMarker(String? eventId)` — for read receipts

### Event API
- `Event.originServerTs` is **`DateTime`**, not `int` — use `.millisecondsSinceEpoch` for timestamps
- `Event.content` is `Map<String, dynamic>`, use `.tryGet('key')` for safe access
- `Event.eventId` is `String?`

### Client.onEvent Stream
The primary mechanism for receiving live events:
```dart
client.onEvent.stream.listen((EventUpdate update) {
  // update.type: EventUpdateType (timeline, state, history, etc.)
  // update.roomID: String
  // update.content: Map<String, dynamic> (full event JSON)
  //   content['type'] — event type like 'm.room.message'
  //   content['content'] — event content map
  //   content['sender'] — sender MXID
  //   content['event_id'] — event ID string
});
```

### User Directory
```dart
final response = await client.searchUserDirectory(query);
// response is SearchUserDirectoryResponse
// response.results is List<Profile>
// Profile has: userId (String), displayName (String?), avatarUrl (Uri?)
```

### Create Room
```dart
final roomId = await client.createRoom(name: ..., invite: [...], ...);
// Returns String (room ID) directly — NOT a response object
```

### Direct Chat
```dart
final roomId = await client.startDirectChat(userId);
// Handles finding existing DM, creating new one, encryption setup
```

---

## Riverpod Providers

| Provider | Type | Purpose |
|---|---|---|
| `authNotifierProvider` | `StateNotifierProvider<AuthNotifier, AuthState>` | Login/logout/restore flow |
| `roomListProvider` | `StreamProvider<List<Room>>` | Live room list from sync |
| `roomListLoadingProvider` | `Provider<bool>` | True while auth unknown |
| `chatNotifierProvider(roomId)` | `StateNotifierProvider.family<ChatNotifier, ChatState, String>` | Per-room chat state + event listener |
| `userSearchProvider(query)` | `FutureProvider.family<List<Profile>, String>` | User directory search |
| `sharedPreferencesProvider` | `Provider<SharedPreferences>` | Defined in `core/services/shared_preferences_provider.dart`, overridden in `main()` |
| `activeRoomIdProvider` | `StateProvider<String?>` | Tracks selected room in responsive split-view |

---

## Router (go_router)

| Path | Widget | Auth Required |
|---|---|---|
| `/login` | `HomeserverPickerView` | No |
| `/settings` | `SettingsScreen` | Yes |
| `/rooms` | `ResponsiveScaffold` (3/2/1-column adaptive) | Yes |
| `/rooms/:roomId/chat` | `ChatScreen(roomId:, roomName:)` | Yes |

`routerProvider` watches `authNotifierProvider` and redirects:
- unauthenticated → `/login`
- authenticated → `/rooms`

On desktop (width > 900px): 3-column layout with NavigationRail + RoomListPanel + ChatPanel.
Room taps update `activeRoomIdProvider` instead of navigating.
On mobile (width < 600px): single-pane, room taps navigate via GoRouter.

---

## Responsive Layout Breakpoints

| Breakpoint | Layout | Components |
|---|---|---|
| > 900px | 3-column | NavigationRail (collapsible) + RoomListPanel + ChatPanel |
| 600–900px | 2-column | RoomListPanel + ChatPanel (split equally) |
| < 600px | 1-column | Full-screen RoomListPanel, navigation via GoRouter |

---

## Urgent Notification Gate

1. Client sends `org.custom.urgency: "urgent"` in event content
2. Server push rule (`.org.custom.urgency`) matches `content.org.custom.urgency == "urgent"` → `notify` with sound+highlight
3. Push rule is auto-setup via `PushRuleService.setupUrgentRule()` after login
4. Other events muted by default push rule
5. Client display: urgent = crimson 2px border + siren glyph
6. Input: long-press send button toggles urgent mode (pulse animation, haptics)

---

## Build Environment

```bash
export ANDROID_HOME=~/Android/Sdk
export JAVA_HOME=~/jdk21
export PATH="$HOME/flutter/bin:$PATH"
flutter build apk --release --no-tree-shake-icons
# Optionally with GITHUB_PAT for crash reporting:
# GITHUB_PAT=ghp_xxx flutter build apk --release --no-tree-shake-icons --dart-define=GITHUB_PAT=$GITHUB_PAT
# Output: build/app/outputs/flutter-apk/app-release.apk
```

- Flutter 3.44, JDK 21, Android SDK 36, NDK 28.2.13676358
- Keystore: `android/app/samchat-keystore.jks` (RSA 2048, 10,000 days)
- Signing: configured in `android/app/build.gradle.kts` via `key.properties`
- `applicationId`: `com.samchat.app`, Namespace: `com.samchat.app`

### Multi-Platform Builds

Build scripts are in `scripts/`:

```bash
# Android (APK universal + per-abi + AAB)
./scripts/build-android.sh

# Linux (tarball)
./scripts/build-linux.sh

# Windows (zip)
./scripts/build-windows.sh

# macOS (DMG)
./scripts/build-macos.sh

# Full release (version bump → build → tag → GitHub Release)
./scripts/release.sh
```

### CI/CD Pipeline

- **`.github/workflows/ci.yml`**: Runs `flutter analyze --no-fatal-infos` and `flutter test` on every push/PR
- **`.github/workflows/release.yml`**: Triggered on `v*` tag push; builds Android, Linux, Windows, macOS in parallel, generates checksums, creates GitHub Release with all artifacts

### Firebase Push Notifications

FCM is wired in `lib/main.dart` with foreground and background handlers routing to `PushGateway.handleRemoteMessage()`. To enable push in production:

1. Place `google-services.json` in `android/app/`
2. Place `GoogleService-Info.plist` in `ios/Runner/`
3. Build and run — push will be active automatically

These files contain sensitive credentials and must not be committed to the repository.

---

## Git & Release Workflow

- Every change (even minor bugfix) must be committed **and** tagged as a new GitHub release.
- Version in `pubspec.yaml` must match the tag.
- Release title: `vX.Y.Z` with changelog in release body.
- APK must be attached to each release.
- After each release, update `AGENTS.md`, `PROJECT.md`, and `.opencode/instructions.md` to reflect the latest state.

---

## Known Blockers / What's Missing

### Working (v0.6.2)
- [x] **Firebase Cloud Messaging (FCM) push notifications**: Foreground + background handlers wired to `PushGateway` for dual-channel urgent/silent push routing
- [x] **iOS platform scaffolding**: Xcode project generated for Swift Package Manager resolution on macOS GHA builds
- [x] **CI/CD pipeline fixes**: Android keystore path, Windows zip syntax, Linux webkit2gtk-4.1 dependency, `flutter analyze --no-fatal-infos`

### Working (v0.6.1)
- [x] **Timeline pagination**: `requestHistory()` loaded when entering a room, scroll-up backfill
- [x] **SamiCodex**: Developer preferences and coding philosophies codex (`.opencode/samicodex.md`)
- [x] **Multi-platform build scripts**: Android APK/AAB, Linux, Windows, macOS packaging scripts
- [x] **Local release orchestration**: `./scripts/release.sh` automated semantic version bumps, changelogs, builds, git tagging, and GitHub Releases
- [x] **CI/CD pipeline**: GitHub Actions for analyze/test (`ci.yml`) and tag-push releases (`release.yml`)
- [x] **Settings screen**: Full settings page with Appearance, Notifications, Privacy, Chat, About sections
- [x] **Dynamic accent colors**: 8 color options (blue, crimson, purple, green, orange, yellow, teal, pink)
- [x] **Theme modes**: Dark/Light/System with persistent selection
- [x] **Bubble style picker**: Modern/Rounded/Compact bubble corner options
- [x] **Notification toggles**: Urgent sound + silent vibration
- [x] **Privacy toggles**: Read receipts + typing indicators
- [x] **Chat settings**: Font size slider + enter-to-send toggle
- [x] **Open source licenses**: Built-in license viewer

### Working (v0.5.0)
- [x] Matrix login + session persistence + restore on cold start
- [x] Push rule `.org.custom.urgency` auto-setup after login
- [x] Background sync via SDK
- [x] Room list sorted by last event, unread badges, timestamps
- [x] New DM (user directory search) + New Group + Join Room
- [x] Chat send via raw HTTP (injects `org.custom.urgency`)
- [x] Receive messages via `client.onEvent` stream (timeline wired)
- [x] Read markers sent on entering chat room
- [x] Logout via AppBar PopupMenu
- [x] Silent/Urgent toggle (long-press send, pulse animation, haptics)
- [x] MSC2545 sticker picker keyboard
- [x] Dual-channel local notifications (HIGH urgent / LOW silent)
- [x] OLED-dark theme
- [x] Retry Sync button on error
- [x] Build succeeds
- [x] **Responsive 3-column layout**: Desktop NavigationRail + RoomListPanel + ChatPanel
- [x] **Responsive 2-column tablet layout**: Side-by-side room list + chat
- [x] **Responsive mobile layout**: Single-pane with GoRouter navigation
- [x] **Collapsible NavigationRail**: Toggles between icon-only (68px) and labeled (200px)
- [x] **FluffyChat-inspired login screen**: Scrollable server card list with custom server expand
- [x] **Clustered message group rendering**: Same-sender messages within 5 min chained under one avatar header
- [x] **Connected bubble radii**: Chained appearance with adjusted corner radii per position
- [x] **Urgent marks stay within groups**: Crimson border + siren chip inline in grouped messages
- [x] **OIDC/SSO login**: `flutter_web_auth_2` SSO flow for servers supporting `m.login.sso`/`oauth2`
- [x] **Network-resilient auth**: SocketException handling, `disconnected` state, `retryConnection()`, login timeout, session restore timeout
- [x] **Login flow probes server**: Detects password/SSO support via `getLoginFlows()` and shows appropriate form
- [x] **Android permissions**: INTERNET + ACCESS_NETWORK_STATE; `flutter_web_auth_2` CallbackActivity for SSO redirect
- [x] **Bug reporting system**: Global `FlutterError.onError` + `PlatformDispatcher.onError` capture; enqueues crash reports + telemetry to `SharedPreferences`; flushes to GitHub Issues via PAT
- [x] **Telemetry service**: Periodic snapshots (5min heartbeat + 12h digest) of sync health, message delivery, login events

### Still Missing
- [ ] **Encryption**: No `m.room.encrypted` handling
- [ ] **Reactions / edits / replies**: Not supported
- [ ] **Error handling**: Inconsistent (some SnackBars, others silent)
- [ ] **No real tests**: Only default Flutter counter test
