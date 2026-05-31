import 'package:matrix/matrix.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const _keyHomeserver = 'samchat_homeserver';
  static const _keyAccessToken = 'samchat_access_token';
  static const _keyUserId = 'samchat_user_id';
  static const _keyDeviceId = 'samchat_device_id';

  static Future<AuthSession?> restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final homeserver = prefs.getString(_keyHomeserver);
    final accessToken = prefs.getString(_keyAccessToken);
    final userId = prefs.getString(_keyUserId);
    final deviceId = prefs.getString(_keyDeviceId);
    if (homeserver == null ||
        accessToken == null ||
        userId == null ||
        deviceId == null) {
      return null;
    }
    return AuthSession(
      homeserver: homeserver,
      accessToken: accessToken,
      userId: userId,
      deviceId: deviceId,
    );
  }

  static Future<Client> loginWithSession(AuthSession session) async {
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
    return client;
  }

  static Future<Client> login({
    required String homeserver,
    required String username,
    required String password,
  }) async {
    final client = Client('SamChat');
    await client.checkHomeserver(Uri.parse(homeserver));
    await client.login(
      LoginType.mLoginPassword,
      identifier: AuthenticationUserIdentifier(user: username),
      password: password,
      initialDeviceDisplayName: 'SamChat',
    );
    return client;
  }

  static Future<void> persistSession(Client client) async {
    final prefs = await SharedPreferences.getInstance();
    final hs = client.homeserver?.toString() ?? '';
    final token = client.accessToken ?? '';
    final uid = client.userID ?? '';
    final did = client.deviceID ?? '';
    await prefs.setString(_keyHomeserver, hs);
    await prefs.setString(_keyAccessToken, token);
    await prefs.setString(_keyUserId, uid);
    await prefs.setString(_keyDeviceId, did);
  }

  static Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyHomeserver);
    await prefs.remove(_keyAccessToken);
    await prefs.remove(_keyUserId);
    await prefs.remove(_keyDeviceId);
  }
}

class AuthSession {
  final String homeserver;
  final String accessToken;
  final String userId;
  final String deviceId;

  const AuthSession({
    required this.homeserver,
    required this.accessToken,
    required this.userId,
    required this.deviceId,
  });
}
