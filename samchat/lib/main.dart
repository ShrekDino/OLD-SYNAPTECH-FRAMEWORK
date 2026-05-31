import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'app.dart';
import 'core/services/github_config.dart';
import 'core/services/github_issue_service.dart';
import 'core/services/connectivity_queue.dart';
import 'core/services/crash_reporter.dart';
import 'core/services/telemetry_service.dart';
import 'core/services/shared_preferences_provider.dart';
import 'features/notifications/notification_channels.dart';
import 'features/notifications/push_gateway.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  await NotificationChannels.init();
  await PushGateway().handleRemoteMessage(message.data);
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    PushGateway().handleRemoteMessage(message.data);
  });

  final config = GitHubConfig.fromEnvironment();

  if (config.isConfigured) {
    final queue = ConnectivityQueue();
    final issueService = GitHubIssueService(
      repoOwner: config.repoOwner,
      repoName: config.repoName,
      pat: config.pat!,
      queue: queue,
    );

    final crashReporter = CrashReporter(issueService);
    crashReporter.install();

    final telemetry = TelemetryService(issueService);
    telemetry.start();

    await queue.flush();
  }

  await NotificationChannels.init();
  final prefs = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(prefs),
      ],
      child: const SamChatApp(),
    ),
  );
}
