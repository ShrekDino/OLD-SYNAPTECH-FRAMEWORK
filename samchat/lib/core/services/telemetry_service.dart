import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/device_identity.dart';
import '../models/telemetry_report.dart';
import 'github_issue_service.dart';

class TelemetryService {
  final GitHubIssueService _service;
  Timer? _heartbeatTimer;
  Timer? _digestTimer;

  int _syncDisconnectCount = 0;
  int _loginAttempts = 0;
  int _messagesSent = 0;
  int _messagesFailed = 0;

  final DateTime _startTime = DateTime.now();

  TelemetryService(this._service);

  void start() {
    _heartbeatTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _logHeartbeat(),
    );

    _digestTimer = Timer.periodic(
      const Duration(hours: 12),
      (_) => _sendDigest(),
    );

    debugPrint('[TelemetryService] Started');
  }

  void stop() {
    _heartbeatTimer?.cancel();
    _digestTimer?.cancel();
    debugPrint('[TelemetryService] Stopped');
  }

  void recordLoginAttempt() => _loginAttempts++;
  void recordSyncDisconnect() => _syncDisconnectCount++;
  void recordMessageSent() => _messagesSent++;
  void recordMessageFailed() => _messagesFailed++;

  Future<void> _logHeartbeat() async {
    debugPrint('[TelemetryService] Heartbeat: '
        '${DateTime.now().difference(_startTime).inMinutes}min up, '
        '$_syncDisconnectCount disconnects, $_messagesSent sent');
  }

  Future<void> _sendDigest() async {
    final device = await DeviceIdentity.capture();
    await _service.reportTelemetry(TelemetrySnapshot(
      uptimeMinutes: DateTime.now().difference(_startTime).inMinutes,
      syncDisconnectCount: _syncDisconnectCount,
      loginAttempts: _loginAttempts,
      messagesSent: _messagesSent,
      messagesFailed: _messagesFailed,
      timestamp: DateTime.now(),
      device: device,
    ));

    _syncDisconnectCount = 0;
    _loginAttempts = 0;
    _messagesSent = 0;
    _messagesFailed = 0;
  }
}
