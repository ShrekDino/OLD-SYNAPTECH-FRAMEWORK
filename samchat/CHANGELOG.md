# Changelog

All notable changes to SamChat are documented here.

## [0.6.2] — 2026-05-23

### Added
- Firebase Cloud Messaging (FCM) push notifications — foreground and
  background message handlers wired to `PushGateway` for dual-channel
  urgent/silent routing
- iOS platform scaffolding — enables Xcode Swift Package Manager resolution
  for macOS builds on GitHub Actions
- `google-services.json` and `GoogleService-Info.plist` credential placeholders
  documented for production push setup

### Fixed
- GitHub Actions release pipeline — Android keystore path mismatch resolved
- GitHub Actions Windows build — PowerShell zip packaging syntax corrected
- GitHub Actions Linux build — added `libwebkit2gtk-4.1-dev` dependency
- GitHub Actions CI — `flutter analyze` now uses `--no-fatal-infos` to
  prevent info-level lints from blocking builds

### Changed
- Bumped pubspec version to `0.6.2`

## [0.6.1] — 2026-05-23

### Added
- Timeline pagination — historical messages from other clients now appear
  when entering a room, with infinite scroll to load more
- Professional release pipeline — GitHub Actions CI/CD, multi-platform
  builds (Android APK/AAB, Linux, Windows, macOS), signed releases with
  checksums
- SamiCodex — project philosophy and coding preferences document

### Fixed
- Version string in settings → licenses screen (`0.5.0` → `0.6.0`)
- Version string in device identity capture (`0.4.0` → `0.6.0`)
- Circular import in `settings_provider.dart` — extracted
  `sharedPreferencesProvider` to its own file

### Removed
- Dead code: `message_bubble.dart` (386 lines, replaced by
  `chat_bubble_group.dart`)
- Empty placeholder: `matrix_client.dart`

## [0.6.0] — 2026-05-23

### Added
- Full settings screen with 5 sections and 12 controls
- 8 dynamic accent colors (blue, crimson, purple, green, orange, yellow,
  teal, pink) — ThemeData regenerates and MaterialApp rebuilds on change
- Dark / Light / System theme modes with persistent selection
- Bubble style picker (Modern / Rounded / Compact corner options)
- Notification toggles: urgent sound + silent vibration
- Privacy toggles: read receipts + typing indicators
- Chat settings: font size slider (12–24pt) + enter-to-send toggle
- Open source license viewer
- Dynamic ThemeData driven by accent color with ValueKey rebuild

## [0.5.0] — 2026-05-22

### Added
- Responsive 3-column desktop layout (NavigationRail + room list + chat)
- Responsive 2-column tablet layout (side-by-side room list + chat)
- Responsive mobile layout (single-pane with GoRouter navigation)
- Collapsible NavigationRail — animated toggle between icon-only and labeled
- FluffyChat-inspired homeserver picker with scrollable server card list
- Clustered message group rendering (same-sender within 5 min)
- Connected bubble radii (first/middle/last position in group)
- Urgent marks rendered inside message groups
- OIDC/SSO login via `flutter_web_auth_2`
- Network-resilient auth — SocketException handling, disconnected state,
  retryConnection(), login timeout, session restore timeout
- Login flow probes server and shows password or SSO form accordingly
- Android permissions for `flutter_web_auth_2` CallbackActivity
- Bug reporting system — FlutterError + PlatformDispatcher capture, queues
  to SharedPreferences, flushes to GitHub Issues
- Telemetry service — 5min heartbeat + 12h digest of sync health, message
  delivery, login events

### Changed
- Bumped compileSdk to 36, targetSdk to 36, NDK to 28.2.13676358
- Upgraded to Kotlin 2.x with JVM 17 target
- Added `--no-tree-shake-icons` flag for Material icon fix

## [0.4.0] — 2026-05-21

### Added
- Crash reporter enqueues reports to SharedPreferences with connectivity queue
- GitHub Issues integration for automatic crash report submission
- OIDC login token flow fixed (extract loginToken from callback URI)
- Pulse animation + haptic feedback on urgent long-press send
- Telemetry service with periodic snapshots
- Pink accent color added to avatar palette
- Material icon fix via `--no-tree-shake-icons` and `cupertino_icons`

### Changed
- Session restore now saves and uses deviceId

## [0.3.0] — 2026-05-20

### Added
- Homeserver picker screen — 6 pre-configured servers + custom URL expandable
- Password login form with server probing
- OIDC/SSO login flow via `flutter_web_auth_2`
- Network resilience — SocketException handling, `disconnected` state,
  retryConnection() on auth error
- Login timeout (20s) and session restore timeout (15s)
- Session persistence via SharedPreferences (homeserver + token + userId +
  deviceId)

## [0.2.0] — 2026-05-19

### Added
- Receive messages via `client.onEvent` stream (timeline wired)
- Logout via AppBar PopupMenuButton with confirmation
- Read markers (setReadMarker on room entry)
- Push rule `.org.custom.urgency` auto-setup after login
- Dual-channel local notifications (HIGH urgent / LOW silent)
- Background sync via SDK
- Room list with unread badges and timestamps
- New DM via user directory search
- New Group creation
- Join Room by alias/ID
- Sticker picker keyboard (MSC2545 image packs)
- OLED-dark theme

## [0.1.4] — 2026-05-18

### Added
- opencode auto-config for AI onboarding (`AGENTS.md`, `PROJECT.md`,
  `.opencode/` directory)

## [0.1.3] — 2026-05-18

### Fixed
- Missing `cupertino_icons` dependency (tofu icons)
- Infinite loading spinner on Matrix SDK `backgroundSync` initialization

## [0.1.2] — 2026-05-18

### Changed
- Split single handoff document into `PROJECT.md` (overview) and
  `AGENTS.md` (execution details)

## [0.1.1] — 2026-05-18

### Fixed
- Matrix SDK API mismatches in auth service and event handling
- Build failures due to incorrect Room/Event API usage

### Added
- AGENTS.md handoff document for AI agent context

## [0.1.0] — 2026-05-18

### Added
- Initial release
- Matrix login with homeserver URL + MXID + password
- Session persistence via SharedPreferences
- Background sync
- Message sending via raw HTTP with `org.custom.urgency` field
- Silent / urgent priority toggle on send
- Room list display
- Basic chat UI with dark theme
- Flutter project structure with Riverpod + go_router
- Android signing configuration
