import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

const _uuid = Uuid();
const _keyDeviceId = 'samchat_device_identity_id';

class DeviceIdentity {
  final String deviceId;
  final String model;
  final String osVersion;
  final String appVersion;

  const DeviceIdentity({
    required this.deviceId,
    required this.model,
    required this.osVersion,
    required this.appVersion,
  });

  Map<String, dynamic> toJson() => {
        'device_id': deviceId,
        'model': model,
        'os_version': osVersion,
        'app_version': appVersion,
      };

  static Future<String> _getOrCreateDeviceId() async {
    final prefs = await SharedPreferences.getInstance();
    final existing = prefs.getString(_keyDeviceId);
    if (existing != null && existing.isNotEmpty) return existing;
    final id = _uuid.v4();
    await prefs.setString(_keyDeviceId, id);
    return id;
  }

  static Future<DeviceIdentity> capture({String appVersion = '0.6.2'}) async {
    final deviceId = await _getOrCreateDeviceId();
    return DeviceIdentity(
      deviceId: deviceId,
      model: defaultTargetPlatform.toString(),
      osVersion: _osInfo(),
      appVersion: appVersion,
    );
  }

  static String _osInfo() {
    try {
      return Platform.operatingSystemVersion;
    } catch (_) {
      return 'unknown';
    }
  }
}
