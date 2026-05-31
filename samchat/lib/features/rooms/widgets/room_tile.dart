import 'package:flutter/material.dart';
import '../../../core/design/app_colors.dart';

class RoomTile extends StatelessWidget {
  final String name;
  final String? avatarUrl;
  final String? lastMessage;
  final int unreadCount;
  final DateTime? lastEventTime;
  final bool isDirect;
  final bool isMuted;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;

  const RoomTile({
    super.key,
    required this.name,
    this.avatarUrl,
    this.lastMessage,
    this.unreadCount = 0,
    this.lastEventTime,
    this.isDirect = false,
    this.isMuted = false,
    required this.onTap,
    this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        child: Row(
          children: [
            _Avatar(
              name: name,
              avatarUrl: avatarUrl,
              isDirect: isDirect,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          name,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: SamChatColors.onSurface,
                            fontSize: 16,
                            fontWeight: unreadCount > 0
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                        ),
                      ),
                      if (lastEventTime != null)
                        Text(
                          _formatTime(lastEventTime!),
                          style: TextStyle(
                            color: SamChatColors.onSurfaceDim,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          lastMessage ?? 'No messages yet',
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                          style: TextStyle(
                            color: SamChatColors.onSurfaceDim,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      if (unreadCount > 0)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: SamChatColors.accentUrgent,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            unreadCount > 99 ? '99+' : '$unreadCount',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
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
}

class _Avatar extends StatelessWidget {
  final String name;
  final String? avatarUrl;
  final bool isDirect;

  const _Avatar({
    required this.name,
    this.avatarUrl,
    this.isDirect = false,
  });

  @override
  Widget build(BuildContext context) {
    final initials = name.isNotEmpty
        ? name[0].toUpperCase()
        : '?';

    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: _avatarColor,
        borderRadius: BorderRadius.circular(isDirect ? 24 : 12),
      ),
      child: avatarUrl != null
          ? ClipRRect(
              borderRadius: BorderRadius.circular(isDirect ? 24 : 12),
              child: Image.network(
                avatarUrl!,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Center(
                  child: Text(
                    initials,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            )
          : Center(
              child: Text(
                initials,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
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
