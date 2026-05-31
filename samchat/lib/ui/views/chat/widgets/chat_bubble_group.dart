import 'package:flutter/material.dart';
import '../../../../core/design/app_colors.dart';
import '../../../../core/models/notification_priority.dart';
import '../../../../shared/widgets/urgent_indicator.dart';
import '../../../../features/chat/models/chat_message.dart';

class MessageGroup {
  final String senderId;
  final String? senderName;
  final List<ChatMessage> messages;

  const MessageGroup({
    required this.senderId,
    this.senderName,
    required this.messages,
  });
}

List<MessageGroup> groupMessages(List<ChatMessage> messages) {
  if (messages.isEmpty) return [];
  if (messages.length == 1) {
    return [
      MessageGroup(
        senderId: messages.first.senderId,
        senderName: messages.first.senderName,
        messages: [messages.first],
      ),
    ];
  }

  final chronological = messages.reversed.toList();
  final groups = <MessageGroup>[];
  var currentMessages = <ChatMessage>[chronological.first];

  for (int i = 1; i < chronological.length; i++) {
    final prev = chronological[i - 1];
    final curr = chronological[i];

    if (curr.senderId == prev.senderId &&
        curr.timestamp.difference(prev.timestamp).inMinutes.abs() < 5) {
      currentMessages.add(curr);
    } else {
      groups.add(MessageGroup(
        senderId: currentMessages.first.senderId,
        senderName: currentMessages.first.senderName,
        messages: List.unmodifiable(currentMessages),
      ));
      currentMessages = [curr];
    }
  }

  groups.add(MessageGroup(
    senderId: currentMessages.first.senderId,
    senderName: currentMessages.first.senderName,
    messages: List.unmodifiable(currentMessages),
  ));

  return groups.reversed.toList();
}

String _mxcToHttp(String mxcUrl, String homeserver) {
  if (!mxcUrl.startsWith('mxc://')) return mxcUrl;
  final stripped = mxcUrl.replaceFirst('mxc://', '');
  final parts = stripped.split('/');
  if (parts.length < 2) return mxcUrl;
  return '$homeserver/_matrix/media/v3/download/${parts[0]}/${parts[1]}';
}

String _formatTime(DateTime dt) {
  final now = DateTime.now();
  final diff = now.difference(dt);
  if (diff.inMinutes < 1) return 'now';
  if (diff.inHours < 1) return '${diff.inMinutes}m';
  if (diff.inDays < 1) {
    return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
  if (diff.inDays < 7) return '${diff.inDays}d';
  return '${dt.month}/${dt.day}';
}

class ChatBubbleGroup extends StatelessWidget {
  final MessageGroup group;
  final bool isOwn;
  final String homeserver;
  final bool isFirstGroup;

  const ChatBubbleGroup({
    super.key,
    required this.group,
    required this.isOwn,
    this.homeserver = '',
    this.isFirstGroup = false,
  });

  @override
  Widget build(BuildContext context) {
    final hasMultiple = group.messages.length > 1;

    return Padding(
      padding: EdgeInsets.only(top: isFirstGroup ? 0 : 8),
      child: Column(
        crossAxisAlignment:
            isOwn ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          if (group.senderName != null && !isOwn)
            Padding(
              padding: const EdgeInsets.only(left: 52, bottom: 2),
              child: Text(
                group.senderName!,
                style: TextStyle(
                  color: SamChatColors.onSurfaceDim,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (!isOwn)
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _SenderAvatar(
                    name: group.senderName ?? group.senderId,
                    size: 36,
                  ),
                ),
              if (isOwn) const Spacer(),
              Flexible(
                child: Column(
                  crossAxisAlignment: isOwn
                      ? CrossAxisAlignment.end
                      : CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: group.messages.map((message) {
                    final isLast =
                        message == group.messages.last;
                    final isFirst =
                        message == group.messages.first;
                    return _buildMessage(message, isFirst, isLast, hasMultiple);
                  }).toList(),
                ),
              ),
              if (!isOwn) const Spacer(),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMessage(
      ChatMessage message, bool isFirst, bool isLast, bool hasMultiple) {
    final isUrgent = message.priority == NotificationPriority.urgent;

    if (message.eventType == 'm.sticker' && message.stickerUrl != null) {
      return _StickerMessage(
        message: message,
        isOwn: isOwn,
        isUrgent: isUrgent,
        homeserver: homeserver,
        isFirst: isFirst,
        isLast: isLast,
        hasMultiple: hasMultiple,
      );
    }

    return Padding(
      padding: EdgeInsets.only(
        top: isFirst ? 0 : 2,
      ),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: isOwn ? 320 : 300,
        ),
        decoration: BoxDecoration(
          color: isOwn
              ? SamChatColors.bubbleSent
              : SamChatColors.bubbleReceived,
          borderRadius: _borderRadius(isFirst, isLast, hasMultiple),
          border: isUrgent
              ? Border.all(
                  color: SamChatColors.bubbleBorderUrgent,
                  width: 1.5,
                )
              : null,
          boxShadow: isUrgent
              ? [
                  BoxShadow(
                    color: SamChatColors.accentUrgent.withValues(alpha: 0.08),
                    blurRadius: 8,
                    spreadRadius: 1,
                  ),
                ]
              : null,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (isUrgent)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const UrgentIndicator(size: 12),
                    const SizedBox(width: 4),
                    Text(
                      'URGENT',
                      style: TextStyle(
                        color: SamChatColors.accentUrgent,
                        fontSize: 9,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.1,
                      ),
                    ),
                  ],
                ),
              ),
            Text(
              message.body,
              style: TextStyle(
                color: SamChatColors.onSurface,
                fontSize: 15,
                height: 1.35,
              ),
            ),
            const SizedBox(height: 2),
            _TimeFooter(
              timestamp: message.timestamp,
              isOwn: isOwn,
              isSending: !message.isSent && isOwn,
            ),
          ],
        ),
      ),
    );
  }

  BorderRadius _borderRadius(
      bool isFirst, bool isLast, bool hasMultiple) {
    if (!hasMultiple) {
      return BorderRadius.circular(16);
    }

    if (isOwn) {
      if (isFirst && isLast) return BorderRadius.circular(16);
      if (isFirst) {
        return BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: const Radius.circular(16),
          bottomRight: const Radius.circular(6),
        );
      }
      if (isLast) {
        return BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(6),
          bottomLeft: const Radius.circular(16),
          bottomRight: const Radius.circular(16),
        );
      }
      return BorderRadius.only(
        topLeft: const Radius.circular(16),
        topRight: const Radius.circular(6),
        bottomLeft: const Radius.circular(16),
        bottomRight: const Radius.circular(6),
      );
    } else {
      if (isFirst && isLast) return BorderRadius.circular(16);
      if (isFirst) {
        return BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: const Radius.circular(6),
          bottomRight: const Radius.circular(16),
        );
      }
      if (isLast) {
        return BorderRadius.only(
          topLeft: const Radius.circular(6),
          topRight: const Radius.circular(16),
          bottomLeft: const Radius.circular(16),
          bottomRight: const Radius.circular(16),
        );
      }
      return BorderRadius.only(
        topLeft: const Radius.circular(6),
        topRight: const Radius.circular(16),
        bottomLeft: const Radius.circular(6),
        bottomRight: const Radius.circular(16),
      );
    }
  }
}

class _StickerMessage extends StatelessWidget {
  final ChatMessage message;
  final bool isOwn;
  final bool isUrgent;
  final String homeserver;
  final bool isFirst;
  final bool isLast;
  final bool hasMultiple;

  const _StickerMessage({
    required this.message,
    required this.isOwn,
    required this.isUrgent,
    required this.homeserver,
    required this.isFirst,
    required this.isLast,
    required this.hasMultiple,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(top: isFirst ? 0 : 2),
      child: Column(
        crossAxisAlignment:
            isOwn ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Container(
            constraints: const BoxConstraints(
              maxWidth: 160,
              maxHeight: 160,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: isUrgent
                  ? Border.all(
                      color: SamChatColors.bubbleBorderUrgent,
                      width: 1.5,
                    )
                  : null,
              boxShadow: isUrgent
                  ? [
                      BoxShadow(
                        color:
                            SamChatColors.accentUrgent.withValues(alpha: 0.08),
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ]
                  : null,
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.network(
                _mxcToHttp(message.stickerUrl!, homeserver),
                fit: BoxFit.contain,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  final total = loadingProgress.expectedTotalBytes;
                  final progress =
                      total != null ? loadingProgress.cumulativeBytesLoaded / total : null;
                  return Container(
                    width: 160,
                    height: 160,
                    color: SamChatColors.surface,
                    child: Center(
                      child: CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 2,
                        color: SamChatColors.accentSilent,
                      ),
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: 160,
                    height: 160,
                    color: SamChatColors.surface,
                    child: Icon(
                      Icons.broken_image_outlined,
                      color:
                          SamChatColors.onSurfaceDim.withValues(alpha: 0.4),
                      size: 32,
                    ),
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: 2),
          _TimeFooter(
            timestamp: message.timestamp,
            isOwn: isOwn,
            isSending: !message.isSent && isOwn,
          ),
        ],
      ),
    );
  }
}

class _TimeFooter extends StatelessWidget {
  final DateTime timestamp;
  final bool isOwn;
  final bool isSending;

  const _TimeFooter({
    required this.timestamp,
    required this.isOwn,
    required this.isSending,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          _formatTime(timestamp),
          style: TextStyle(
            color: isOwn
                ? SamChatColors.onSurface.withValues(alpha: 0.6)
                : SamChatColors.onSurfaceDim,
            fontSize: 11,
          ),
        ),
        if (isSending) ...[
          const SizedBox(width: 4),
          const Icon(
            Icons.access_time,
            size: 12,
            color: SamChatColors.onSurfaceDim,
          ),
        ],
      ],
    );
  }
}

class _SenderAvatar extends StatelessWidget {
  final String name;
  final double size;

  const _SenderAvatar({
    required this.name,
    this.size = 36,
  });

  @override
  Widget build(BuildContext context) {
    final initials = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: _avatarColor,
        borderRadius: BorderRadius.circular(size / 2),
      ),
      child: Center(
        child: Text(
          initials,
          style: TextStyle(
            color: Colors.white,
            fontSize: size * 0.45,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }

  Color get _avatarColor {
    final hash = name.hashCode;
    final colors = [
      const Color(0xFF007AFF),
      const Color(0xFF34C759),
      const Color(0xFFFF9500),
      const Color(0xFFAF52DE),
      const Color(0xFFFF2D55),
      const Color(0xFF5856D6),
      const Color(0xFF00C7BE),
      const Color(0xFFFF6482),
    ];
    return colors[hash.abs() % colors.length];
  }
}
