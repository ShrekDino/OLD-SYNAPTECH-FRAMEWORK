import 'dart:convert';
import '../../core/matrix/event_extensions.dart';
import 'notification_service.dart';

class PushPayload {
  final String eventId;
  final String roomId;
  final String sender;
  final Map<String, dynamic> content;
  final String? roomName;
  final String type;

  const PushPayload({
    required this.eventId,
    required this.roomId,
    required this.sender,
    required this.content,
    this.roomName,
    this.type = 'm.room.message',
  });

  bool get isUrgent => content.isUrgentContent;

  bool get isSticker => type == 'm.sticker';

  String get bodyText {
    if (isSticker) return '[Sticker]';
    return content['body'] as String? ?? 'New message';
  }
}

class PushGateway {
  final NotificationService _notificationService = NotificationService();

  PushGateway();

  Future<void> handleRemoteMessage(Map<String, dynamic> data) async {
    try {
      final payload = _parsePayload(data);
      if (payload == null) return;

      await _routeNotification(payload);
    } catch (e) {
      print('PushGateway: failed to handle message: $e');
    }
  }

  PushPayload? _parsePayload(Map<String, dynamic> data) {
    final eventId = data['event_id'] as String?;
    final roomId = data['room_id'] as String?;
    final sender = data['sender'] as String?;

    if (eventId == null || roomId == null || sender == null) return null;

    final eventType = data['type'] as String? ?? 'm.room.message';

    Map<String, dynamic>? content;
    final rawContent = data['content'];
    if (rawContent is Map<String, dynamic>) {
      content = rawContent;
    } else if (rawContent is String) {
      try {
        content = jsonDecode(rawContent) as Map<String, dynamic>;
      } catch (_) {}
    }

    content ??= <String, dynamic>{};

    return PushPayload(
      eventId: eventId,
      roomId: roomId,
      sender: sender,
      content: content,
      roomName: data['room_name'] as String?,
      type: eventType,
    );
  }

  Future<void> _routeNotification(PushPayload payload) async {
    final notificationId = payload.eventId.hashCode;
    final title = payload.roomName ?? payload.sender;
    final body = payload.bodyText;

    if (payload.isUrgent) {
      await _notificationService.showUrgent(
        id: notificationId,
        title: '${payload.sender} via $title',
        body: body,
        payload: jsonEncode({
          'room_id': payload.roomId,
          'event_id': payload.eventId,
          'urgent': true,
        }),
      );
    } else {
      await _notificationService.showSilent(
        id: notificationId,
        title: title,
        body: body,
        payload: jsonEncode({
          'room_id': payload.roomId,
          'event_id': payload.eventId,
          'urgent': false,
        }),
      );
    }
  }
}

PushGateway createPushGateway() => PushGateway();
