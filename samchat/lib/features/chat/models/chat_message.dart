import '../../../core/models/notification_priority.dart';

class ChatMessage {
  final String id;
  final String roomId;
  final String senderId;
  final String body;
  final NotificationPriority priority;
  final DateTime timestamp;
  final bool isSent;
  final bool isRemote;
  final String? senderName;
  final String? eventType;
  final String? stickerUrl;

  const ChatMessage({
    required this.id,
    required this.roomId,
    required this.senderId,
    required this.body,
    this.priority = NotificationPriority.silent,
    required this.timestamp,
    this.isSent = false,
    this.isRemote = false,
    this.senderName,
    this.eventType,
    this.stickerUrl,
  });

  ChatMessage copyWith({
    String? id,
    String? roomId,
    String? senderId,
    String? body,
    NotificationPriority? priority,
    DateTime? timestamp,
    bool? isSent,
    bool? isRemote,
    String? senderName,
    String? eventType,
    String? stickerUrl,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      roomId: roomId ?? this.roomId,
      senderId: senderId ?? this.senderId,
      body: body ?? this.body,
      priority: priority ?? this.priority,
      timestamp: timestamp ?? this.timestamp,
      isSent: isSent ?? this.isSent,
      isRemote: isRemote ?? this.isRemote,
      senderName: senderName ?? this.senderName,
      eventType: eventType ?? this.eventType,
      stickerUrl: stickerUrl ?? this.stickerUrl,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'room_id': roomId,
        'sender_id': senderId,
        'body': body,
        'priority': priority.name,
        'timestamp': timestamp.toIso8601String(),
        'is_sent': isSent,
        'is_remote': isRemote,
        'sender_name': senderName,
        'event_type': eventType,
        'sticker_url': stickerUrl,
      };

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: json['id'] as String,
        roomId: json['room_id'] as String,
        senderId: json['sender_id'] as String,
        body: json['body'] as String,
        priority: NotificationPriority.fromJson(json['priority'] as String),
        timestamp: DateTime.parse(json['timestamp'] as String),
        isSent: json['is_sent'] as bool? ?? false,
        isRemote: json['is_remote'] as bool? ?? false,
        senderName: json['sender_name'] as String?,
        eventType: json['event_type'] as String?,
        stickerUrl: json['sticker_url'] as String?,
      );

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ChatMessage &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'ChatMessage(id: $id, body: $body, priority: $priority)';
}
