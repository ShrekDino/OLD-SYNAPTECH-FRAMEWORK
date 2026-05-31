import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/device_identity.dart';
import '../models/telemetry_report.dart';
import 'github_issue_service.dart';

class CrashReporter {
  final GitHubIssueService _service;
  final Set<int> _recentHashes = {};
  static const _dedupWindowMs = 30000;

  CrashReporter(this._service);

  void install() {
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.dumpErrorToConsole(details);
      _handle(details.exceptionAsString(), details.stack ?? StackTrace.empty);
    };
  }

  void _handle(String exception, StackTrace stack) {
    final hash = exception.hashCode ^ stack.hashCode;
    if (_recentHashes.contains(hash)) return;
    _recentHashes.add(hash);
    Timer(const Duration(milliseconds: _dedupWindowMs), () => _recentHashes.remove(hash));

    DeviceIdentity.capture().then((device) {
      _service.reportCrash(CrashReport(
        type: 'FlutterError',
        exception: exception.length > 200 ? exception.substring(0, 200) : exception,
        stackTrace: stack.toString().length > 2000
            ? stack.toString().substring(0, 2000)
            : stack.toString(),
        route: '',
        authStatus: 'unknown',
        timestamp: DateTime.now(),
        device: device,
      ));
    });
  }
}
