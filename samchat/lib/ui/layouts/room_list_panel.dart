import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:matrix/matrix.dart';
import '../../core/design/app_colors.dart';
import '../../features/auth/state/auth_notifier.dart';
import '../../features/rooms/providers/room_list_provider.dart';
import '../../features/rooms/widgets/room_tile.dart';

class RoomListPanel extends ConsumerWidget {
  final void Function(Room room)? onRoomTap;

  const RoomListPanel({super.key, this.onRoomTap});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final roomsAsync = ref.watch(roomListProvider);
    final authState = ref.watch(authNotifierProvider);

    return roomsAsync.when(
      loading: () => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              authState.status == AuthStatus.restoring
                  ? 'Restoring session...'
                  : 'Connecting...',
              style: TextStyle(
                color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
      error: (error, stack) {
        debugPrint('[RoomListPanel] error: $error\n$stack');
        return Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.cloud_off_rounded,
                  size: 48,
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                ),
                const SizedBox(height: 16),
                Text(
                  'Could not load rooms',
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  error.toString(),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 24),
                FilledButton.icon(
                  onPressed: () {
                    ref.invalidate(roomListProvider);
                  },
                  icon: const Icon(Icons.refresh_rounded, size: 18),
                  label: const Text('Retry Sync'),
                  style: FilledButton.styleFrom(
                    backgroundColor: SamChatColors.accentSilent,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
      data: (rooms) {
        if (rooms.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 48,
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                ),
                const SizedBox(height: 16),
                Text(
                  'No conversations yet',
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Tap + to start a new chat',
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.separated(
          itemCount: rooms.length,
          separatorBuilder: (context, index) => Divider(
            height: 0.5,
            color: SamChatColors.divider,
            indent: 76,
          ),
          itemBuilder: (context, index) {
            final room = rooms[index];
            final displayName = room.getLocalizedDisplayname();

            return RoomTile(
              name: room.name.isNotEmpty ? room.name : displayName,
              avatarUrl: room.avatar?.toString(),
              lastMessage:
                  room.lastEvent?.content.tryGet('body') as String?,
              unreadCount: room.notificationCount,
              lastEventTime: room.lastEvent?.originServerTs,
              isDirect: room.isDirectChat,
              onTap: () {
                if (onRoomTap != null) {
                  onRoomTap!(room);
                } else {
                  context.go(
                    '/rooms/${Uri.encodeComponent(room.id)}/chat',
                    extra: room.name.isNotEmpty ? room.name : displayName,
                  );
                }
              },
            );
          },
        );
      },
    );
  }
}
