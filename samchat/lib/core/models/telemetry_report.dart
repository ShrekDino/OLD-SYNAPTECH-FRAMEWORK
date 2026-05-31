import 'device_identity.dart';

enum ReportType { crash, syncAnomaly, loginFailure, telemetryHeartbeat }

class CrashReport {
  final String type;
  final String exception;
  final String stackTrace;
  final String route;
  final String authStatus;
  final DateTime timestamp;
  final DeviceIdentity device;

  const CrashReport({
    required this.type,
    required this.exception,
    required this.stackTrace,
    required this.route,
    required this.authStatus,
    required this.timestamp,
    required this.device,
  });

  Map<String, dynamic> toJson() => {
        'report_type': 'crash',
        'type': type,
        'exception': exception,
        'stack_trace': stackTrace,
        'route': route,
        'auth_status': authStatus,
        'timestamp': timestamp.toIso8601String(),
        'device': device.toJson(),
      };
}

class LoginReport {
  final bool success;
  final String method;
  final String? homeserver;
  final String? error;
  final DateTime timestamp;
  final DeviceIdentity device;

  const LoginReport({
    required this.success,
    required this.method,
    this.homeserver,
    this.error,
    required this.timestamp,
    required this.device,
  });

  Map<String, dynamic> toJson() => {
        'report_type': 'login',
        'success': success,
        'method': method,
        'homeserver': homeserver,
        'error': error,
        'timestamp': timestamp.toIso8601String(),
        'device': device.toJson(),
      };
}

class SyncReport {
  final String state;
  final int durationSeconds;
  final String? error;
  final DateTime timestamp;
  final DeviceIdentity device;

  const SyncReport({
    required this.state,
    required this.durationSeconds,
    this.error,
    required this.timestamp,
    required this.device,
  });

  Map<String, dynamic> toJson() => {
        'report_type': 'sync',
        'state': state,
        'duration_seconds': durationSeconds,
        'error': error,
        'timestamp': timestamp.toIso8601String(),
        'device': device.toJson(),
      };
}

class TelemetrySnapshot {
  final int uptimeMinutes;
  final int syncDisconnectCount;
  final int loginAttempts;
  final int messagesSent;
  final int messagesFailed;
  final double? memoryMb;
  final DateTime timestamp;
  final DeviceIdentity device;

  const TelemetrySnapshot({
    required this.uptimeMinutes,
    required this.syncDisconnectCount,
    required this.loginAttempts,
    required this.messagesSent,
    required this.messagesFailed,
    this.memoryMb,
    required this.timestamp,
    required this.device,
  });

  Map<String, dynamic> toJson() => {
        'report_type': 'telemetry',
        'uptime_minutes': uptimeMinutes,
        'sync_disconnect_count': syncDisconnectCount,
        'login_attempts': loginAttempts,
        'messages_sent': messagesSent,
        'messages_failed': messagesFailed,
        'memory_mb': memoryMb,
        'timestamp': timestamp.toIso8601String(),
        'device': device.toJson(),
      };
}
