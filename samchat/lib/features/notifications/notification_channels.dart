import 'dart:typed_data';
import 'dart:ui';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

abstract final class NotificationChannels {
  NotificationChannels._();

  static const String urgentChannelId = 'samchat_urgent';
  static const String silentChannelId = 'samchat_silent';
  static const String urgentChannelName = 'Urgent Messages';
  static const String silentChannelName = 'Messages';

  static Future<void> init() async {
    final plugin = FlutterLocalNotificationsPlugin();

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    await plugin.initialize(
      const InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      ),
    );

    final androidPlugin =
        plugin.resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();

    if (androidPlugin != null) {
      await androidPlugin.createNotificationChannel(
        AndroidNotificationChannel(
          urgentChannelId,
          urgentChannelName,
          description: 'Time-sensitive urgent messages that bypass silent mode',
          importance: Importance.high,
          playSound: true,
          enableVibration: true,
          enableLights: true,
          ledColor: Color(0xFFFF3B30),
          vibrationPattern: Int64List.fromList([0, 200, 100, 200, 100, 400]),
          showBadge: true,
        ),
      );

      await androidPlugin.createNotificationChannel(
        AndroidNotificationChannel(
          silentChannelId,
          silentChannelName,
          description:
              'Standard silent-by-default messages — no sound, no heads-up',
          importance: Importance.low,
          playSound: false,
          enableVibration: false,
          enableLights: false,
          showBadge: true,
        ),
      );
    }
  }
}
