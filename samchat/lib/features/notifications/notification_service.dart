import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'notification_channels.dart';

class NotificationService {
  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();

  static final NotificationService _instance = NotificationService._();
  factory NotificationService() => _instance;
  NotificationService._();

  bool _initialized = false;

  Future<void> ensureInitialized() async {
    if (!_initialized) {
      await NotificationChannels.init();
      _initialized = true;
    }
  }

  Future<void> showUrgent({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    await ensureInitialized();

    await _plugin.show(
      id,
      '🚨 $title',
      body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          NotificationChannels.urgentChannelId,
          NotificationChannels.urgentChannelName,
          channelDescription:
              'Time-sensitive urgent messages that bypass silent mode',
          importance: Importance.high,
          priority: Priority.high,
          fullScreenIntent: true,
          category: AndroidNotificationCategory.alarm,
          visibility: NotificationVisibility.public,
          actions: <AndroidNotificationAction>[
            AndroidNotificationAction('open_room', 'Open', showsUserInterface: true),
          ],
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
          sound: 'default.wav',
          interruptionLevel: InterruptionLevel.timeSensitive,
          categoryIdentifier: 'urgent_message',
        ),
      ),
      payload: payload,
    );
  }

  Future<void> showSilent({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    await ensureInitialized();

    await _plugin.show(
      id,
      title,
      body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          NotificationChannels.silentChannelId,
          NotificationChannels.silentChannelName,
          channelDescription:
              'Standard silent-by-default messages — no sound, no heads-up',
          importance: Importance.low,
          priority: Priority.low,
          playSound: false,
          enableVibration: false,
          showWhen: false,
          visibility: NotificationVisibility.private,
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: false,
          presentBadge: true,
          presentSound: false,
          interruptionLevel: InterruptionLevel.passive,
        ),
      ),
      payload: payload,
    );
  }

  Future<void> cancel(int id) async {
    await _plugin.cancel(id);
  }

  Future<void> cancelAll() async {
    await _plugin.cancelAll();
  }

  Future<void> showInsistentUrgent({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    await ensureInitialized();

    final androidDetails = AndroidNotificationDetails(
      NotificationChannels.urgentChannelId,
      NotificationChannels.urgentChannelName,
      channelDescription:
          'Time-sensitive urgent messages that bypass silent mode',
      importance: Importance.max,
      priority: Priority.max,
      fullScreenIntent: true,
      category: AndroidNotificationCategory.alarm,
      visibility: NotificationVisibility.public,
      onlyAlertOnce: false,
      ongoing: true,
      autoCancel: false,
      actions: <AndroidNotificationAction>[
        AndroidNotificationAction('open_room', 'Open', showsUserInterface: true),
        AndroidNotificationAction('dismiss', 'Dismiss'),
      ],
    );

    await _plugin.show(
      id,
      '🚨 URGENT: $title',
      body,
      NotificationDetails(android: androidDetails),
      payload: payload,
    );
  }
}
