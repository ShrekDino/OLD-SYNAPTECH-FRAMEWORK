import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:matrix/matrix.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import '../../../core/matrix/auth_service.dart';
import '../../../core/matrix/push_rule_service.dart';

enum AuthStatus {
  unknown,
  restoring,
  unauthenticated,
  loggingIn,
  loggedIn,
  syncError,
  disconnected,
  error,
}

class AuthState {
  final AuthStatus status;
  final Client? client;
  final String? error;
  final String? userId;
  final String? homeserver;
  final DateTime? lastSyncAttempt;

  const AuthState({
    this.status = AuthStatus.unknown,
    this.client,
    this.error,
    this.userId,
    this.homeserver,
    this.lastSyncAttempt,
  });

  AuthState copyWith({
    AuthStatus? status,
    Client? client,
    String? error,
    String? userId,
    String? homeserver,
    DateTime? lastSyncAttempt,
    bool clearError = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      client: client ?? this.client,
      error: clearError ? null : (error ?? this.error),
      userId: userId ?? this.userId,
      homeserver: homeserver ?? this.homeserver,
      lastSyncAttempt: lastSyncAttempt ?? this.lastSyncAttempt,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  StreamSubscription<SyncStatusUpdate>? _syncStatusSub;
  Timer? _loginTimeout;

  AuthNotifier() : super(const AuthState()) {
    tryRestoreSession();
  }

  @override
  void dispose() {
    _syncStatusSub?.cancel();
    _loginTimeout?.cancel();
    super.dispose();
  }

  Future<void> tryRestoreSession() async {
    state = state.copyWith(status: AuthStatus.restoring);

    try {
      final session = await AuthService.restoreSession()
          .timeout(const Duration(seconds: 15));
      if (session == null) {
        state = state.copyWith(status: AuthStatus.unauthenticated);
        return;
      }

      final client = await AuthService.loginWithSession(session)
          .timeout(const Duration(seconds: 15));
      _startSync(client);
      _setupPushRule(client);
      state = state.copyWith(
        status: AuthStatus.loggedIn,
        client: client,
        userId: client.userID,
        homeserver: client.homeserver?.toString(),
      );
    } on TimeoutException {
      debugPrint('[AuthNotifier] Session restore timed out');
      state = state.copyWith(
        status: AuthStatus.disconnected,
        error: 'Connection timed out. Check your network and retry.',
      );
    } on SocketException catch (e) {
      debugPrint('[AuthNotifier] Network error restoring session: $e');
      state = state.copyWith(
        status: AuthStatus.disconnected,
        error: 'No internet connection. Check your network and retry.',
      );
    } catch (e) {
      debugPrint('[AuthNotifier] Failed to restore session: $e');
      await AuthService.clearSession();
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<Client> validateHomeserver(String homeserverUrl) async {
    final probe = Client('SamChat');
    await probe.checkHomeserver(Uri.parse(homeserverUrl));
    return probe;
  }

  Future<bool> supportsSso(Client probe) async {
    try {
      final loginFlows = await probe.getLoginFlows();
      return loginFlows?.any((f) =>
              f.type == AuthenticationTypes.sso ||
              f.type == AuthenticationTypes.oauth2) ??
          false;
    } catch (_) {
      return false;
    }
  }

  Future<void> loginWithPassword({
    required Client probe,
    required String username,
    required String password,
  }) async {
    state = state.copyWith(
      status: AuthStatus.loggingIn,
      error: null,
      homeserver: probe.homeserver?.toString(),
    );

    _startLoginTimeout();

    try {
      final client = probe;
      await client.login(
        LoginType.mLoginPassword,
        identifier: AuthenticationUserIdentifier(user: username),
        password: password,
        initialDeviceDisplayName: 'SamChat',
      );

      _loginTimeout?.cancel();

      await AuthService.persistSession(client);
      _startSync(client);
      _setupPushRule(client);

      state = state.copyWith(
        status: AuthStatus.loggedIn,
        client: client,
        userId: client.userID,
        error: null,
      );
    } on SocketException catch (e) {
      _loginTimeout?.cancel();
      debugPrint('[AuthNotifier] Network error during login: $e');
      state = state.copyWith(
        status: AuthStatus.disconnected,
        error: 'Cannot reach the server. Check your connection.',
      );
    } on TimeoutException {
      _loginTimeout?.cancel();
      state = state.copyWith(
        status: AuthStatus.disconnected,
        error: 'Connection timed out. The server may be slow or unreachable.',
      );
    } catch (e) {
      _loginTimeout?.cancel();
      final msg = e.toString();
      state = state.copyWith(
        status: AuthStatus.error,
        error: msg.contains('Bad password') || msg.contains('401')
            ? 'Incorrect username or password.'
            : msg,
      );
    }
  }

  Future<void> loginWithSso(Client probe) async {
    state = state.copyWith(
      status: AuthStatus.loggingIn,
      error: null,
      homeserver: probe.homeserver?.toString(),
    );

    final homeserver = probe.homeserver?.toString() ?? '';
    if (homeserver.isEmpty) {
      state = state.copyWith(
        status: AuthStatus.error,
        error: 'Homeserver URL not found.',
      );
      return;
    }

    try {
      const callbackScheme = 'samchat';
      final redirectUrl = '$callbackScheme://login';

      final ssoUrl =
          '$homeserver/_matrix/client/v3/login/sso/redirect?redirectUrl=$redirectUrl';

      final result = await FlutterWebAuth2.authenticate(
        url: ssoUrl,
        callbackUrlScheme: callbackScheme,
      );

      final uri = Uri.parse(result);
      final loginToken = uri.queryParameters['loginToken'];

      if (loginToken == null || loginToken.isEmpty) {
        state = state.copyWith(
          status: AuthStatus.error,
          error: 'SSO login failed — no login token received.',
        );
        return;
      }

      final client = probe;
      await client.login(
        LoginType.mLoginToken,
        token: loginToken,
        initialDeviceDisplayName: 'SamChat',
      );

      await AuthService.persistSession(client);
      _startSync(client);
      _setupPushRule(client);

      state = state.copyWith(
        status: AuthStatus.loggedIn,
        client: client,
        userId: client.userID,
        error: null,
      );
    } on SocketException catch (e) {
      debugPrint('[AuthNotifier] Network error during SSO login: $e');
      state = state.copyWith(
        status: AuthStatus.disconnected,
        error: 'Cannot reach the server. Check your connection.',
      );
    } catch (e) {
      debugPrint('[AuthNotifier] SSO login error: $e');
      if (e.toString().contains('CANCELED') ||
          e.toString().contains('Canceled')) {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      } else {
        state = state.copyWith(
          status: AuthStatus.error,
          error: 'SSO login failed: ${e.toString()}',
        );
      }
    }
  }

  Future<void> retryConnection() async {
    final current = state;
    if (current.client != null) {
      debugPrint('[AuthNotifier] Retrying sync connection...');
      state = state.copyWith(
        status: AuthStatus.restoring,
        error: null,
        lastSyncAttempt: DateTime.now(),
      );
      _startSync(current.client!);
      state = state.copyWith(status: AuthStatus.loggedIn);
      return;
    }
    await tryRestoreSession();
  }

  Future<void> logout() async {
    _syncStatusSub?.cancel();
    try {
      await state.client?.logout();
    } catch (_) {}
    await AuthService.clearSession();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void dismissError() {
    state = state.copyWith(clearError: true);
  }

  void _startSync(Client client) {
    _syncStatusSub?.cancel();
    client.backgroundSync = true;

    _syncStatusSub = client.onSyncStatus.stream.listen(
      (status) {
        if (status.status == SyncStatus.error) {
          final error = status.error;
          if (error != null && error is SocketException) {
            debugPrint('[AuthNotifier] Sync connection lost: $error');
            state = state.copyWith(
              status: AuthStatus.disconnected,
              error: 'Connection lost. Tap Retry to reconnect.',
              lastSyncAttempt: DateTime.now(),
            );
          } else if (error != null) {
            debugPrint('[AuthNotifier] Sync error: $error');
            state = state.copyWith(
              status: AuthStatus.syncError,
              error: error.toString(),
              lastSyncAttempt: DateTime.now(),
            );
          }
        } else if (status.status == SyncStatus.finished) {
          if (state.status == AuthStatus.disconnected) {
            state = state.copyWith(status: AuthStatus.loggedIn);
          }
        }
      },
      onError: (e) {
        debugPrint('[AuthNotifier] Sync status stream error: $e');
      },
    );
  }

  void _startLoginTimeout() {
    _loginTimeout?.cancel();
    _loginTimeout = Timer(const Duration(seconds: 20), () {
      if (state.status == AuthStatus.loggingIn) {
        state = state.copyWith(
          status: AuthStatus.disconnected,
          error: 'Login timed out. The server may be slow or unreachable.',
        );
      }
    });
  }

  void _setupPushRule(Client client) {
    final hs = client.homeserver?.toString() ?? '';
    final token = client.accessToken ?? '';
    if (hs.isEmpty || token.isEmpty) return;
    PushRuleService.setupUrgentRule(
      homeserver: hs,
      accessToken: token,
    ).catchError((e) {
      debugPrint('[AuthNotifier] Failed to setup push rule: $e');
    });
  }
}

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>(
  (ref) => AuthNotifier(),
);
