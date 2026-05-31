import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../auth/state/auth_notifier.dart';
import '../../../ui/layouts/room_list_panel.dart';
import 'new_chat_fab.dart';

class RoomListScreen extends ConsumerWidget {
  const RoomListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: SamChatColors.background,
      appBar: AppBar(
        title: const Text('SamChat'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.settings_outlined),
            onSelected: (value) async {
              if (value == 'logout') {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    backgroundColor: SamChatColors.surfaceElevated,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    title: const Text(
                      'Log out',
                      style: TextStyle(color: SamChatColors.onSurface),
                    ),
                    content: const Text(
                      'Are you sure you want to log out?',
                      style: TextStyle(color: SamChatColors.onSurfaceDim),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(ctx).pop(false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(ctx).pop(true),
                        child: Text(
                          'Log out',
                          style: TextStyle(
                            color: SamChatColors.accentUrgent,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
                if (confirmed == true) {
                  // ignore: use_build_context_synchronously
                  ref.read(authNotifierProvider.notifier).logout();
                }
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout_rounded, size: 18),
                    SizedBox(width: 10),
                    Text('Log out'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: const RoomListPanel(),
      floatingActionButton: NewChatFab(),
    );
  }
}
