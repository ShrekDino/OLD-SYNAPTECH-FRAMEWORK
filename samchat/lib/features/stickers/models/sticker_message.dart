import '../../../core/models/notification_priority.dart';

class StickerMessageContent {
  final String body;
  final String url;
  final Map<String, dynamic> info;
  final NotificationPriority priority;

  const StickerMessageContent({
    required this.body,
    required this.url,
    this.info = const {},
    this.priority = NotificationPriority.silent,
  });

  Map<String, dynamic> toJson() => {
        'body': body,
        'url': url,
        'info': info,
        if (priority.isUrgent) 'org.custom.urgency': 'urgent',
      };

  factory StickerMessageContent.fromJson(Map<String, dynamic> json) {
    final rawInfo = json['info'];
    return StickerMessageContent(
      body: json['body'] as String? ?? '',
      url: json['url'] as String? ?? '',
      info: rawInfo is Map<String, dynamic> ? rawInfo : {},
      priority: json['org.custom.urgency'] == 'urgent'
          ? NotificationPriority.urgent
          : NotificationPriority.silent,
    );
  }
}
