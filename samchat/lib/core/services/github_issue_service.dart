import 'dart:convert';
import '../models/telemetry_report.dart';
import 'connectivity_queue.dart';

class GitHubIssueService {
  final String _repoOwner;
  final String _repoName;
  final String _pat;
  final ConnectivityQueue _queue;

  GitHubIssueService({
    required String repoOwner,
    required String repoName,
    required String pat,
    required ConnectivityQueue queue,
  })  : _repoOwner = repoOwner,
        _repoName = repoName,
        _pat = pat,
        _queue = queue;

  bool get isEnabled => _pat.isNotEmpty;

  Future<void> reportCrash(CrashReport report) async {
    if (!isEnabled) return;
    await _queue.enqueue(
      title: '[crash] ${report.exception} — ${report.device.model}',
      body: _crashBody(report),
      labels: ['crash', 'device:${report.device.deviceId}'],
      repoOwner: _repoOwner,
      repoName: _repoName,
      pat: _pat,
    );
  }

  Future<void> reportLogin(LoginReport report) async {
    if (!isEnabled) return;
    final status = report.success ? 'success' : 'failure';
    await _queue.enqueue(
      title: '[login] $status via ${report.method} — ${report.device.model}',
      body: _loginBody(report),
      labels: ['login', status, 'device:${report.device.deviceId}'],
      repoOwner: _repoOwner,
      repoName: _repoName,
      pat: _pat,
    );
  }

  Future<void> reportSync(SyncReport report) async {
    if (!isEnabled) return;
    await _queue.enqueue(
      title: '[sync] ${report.state} — ${report.device.model}',
      body: _syncBody(report),
      labels: ['sync', 'device:${report.device.deviceId}'],
      repoOwner: _repoOwner,
      repoName: _repoName,
      pat: _pat,
    );
  }

  Future<void> reportTelemetry(TelemetrySnapshot snapshot) async {
    if (!isEnabled) return;
    final date = snapshot.timestamp.toIso8601String().substring(0, 10);
    await _queue.enqueue(
      title: '[telemetry] ${snapshot.device.model} — $date',
      body: _telemetryBody(snapshot),
      labels: ['telemetry', 'device:${snapshot.device.deviceId}'],
      repoOwner: _repoOwner,
      repoName: _repoName,
      pat: _pat,
    );
  }

  String _crashBody(CrashReport r) {
    return '''## Crash Report

**Exception:** ${r.exception}
**Source:** ${r.type}
**Route:** ${r.route}
**Auth Status:** ${r.authStatus}
**Timestamp:** ${r.timestamp.toIso8601String()}

### Stack Trace
\`\`\`
${r.stackTrace}
\`\`\`

### Raw
\`\`\`json
${jsonEncode(r.toJson())}
\`\`\`
''';
  }

  String _loginBody(LoginReport r) {
    return '''## Login Report

**Success:** ${r.success}
**Method:** ${r.method}
**Homeserver:** ${r.homeserver ?? 'unknown'}
**Error:** ${r.error ?? 'none'}
**Timestamp:** ${r.timestamp.toIso8601String()}

\`\`\`json
${jsonEncode(r.toJson())}
\`\`\`
''';
  }

  String _syncBody(SyncReport r) {
    return '''## Sync Report

**State:** ${r.state}
**Duration:** ${r.durationSeconds}s
**Error:** ${r.error ?? 'none'}
**Timestamp:** ${r.timestamp.toIso8601String()}

\`\`\`json
${jsonEncode(r.toJson())}
\`\`\`
''';
  }

  String _telemetryBody(TelemetrySnapshot s) {
    return '''## Telemetry Snapshot

**Uptime:** ${s.uptimeMinutes}min
**Sync Disconnects:** ${s.syncDisconnectCount}
**Login Attempts:** ${s.loginAttempts}
**Messages Sent:** ${s.messagesSent}
**Messages Failed:** ${s.messagesFailed}
**Timestamp:** ${s.timestamp.toIso8601String()}

\`\`\`json
${jsonEncode(s.toJson())}
\`\`\`
''';
  }
}
