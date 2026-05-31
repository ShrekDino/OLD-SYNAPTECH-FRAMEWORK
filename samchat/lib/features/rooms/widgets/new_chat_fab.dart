import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import 'create_group_sheet.dart';
import 'join_room_sheet.dart';
import 'user_search_delegate.dart';

class NewChatFab extends ConsumerWidget {
  const NewChatFab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FloatingActionButton(
      backgroundColor: SamChatColors.accentSilent,
      onPressed: () => _showOptions(context),
      child: const Icon(
        Icons.edit_rounded,
        color: Colors.white,
      ),
    );
  }

  void _showOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: SamChatColors.surfaceElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _OptionTile(
                icon: Icons.person_add_outlined,
                title: 'New private chat',
                subtitle: 'Start a direct message with someone',
                onTap: () {
                  Navigator.pop(context);
                  showSearch(
                    context: context,
                    delegate: UserSearchDelegate(),
                  );
                },
              ),
              _OptionTile(
                icon: Icons.group_add_outlined,
                title: 'New group',
                subtitle: 'Create a group conversation',
                onTap: () {
                  Navigator.pop(context);
                  showModalBottomSheet(
                    context: context,
                    backgroundColor: SamChatColors.surfaceElevated,
                    isScrollControlled: true,
                    shape: const RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.vertical(top: Radius.circular(16)),
                    ),
                    builder: (context) => const CreateGroupSheet(),
                  );
                },
              ),
              _OptionTile(
                icon: Icons.add_box_outlined,
                title: 'Join room',
                subtitle: 'Connect to a public room',
                onTap: () {
                  Navigator.pop(context);
                  showDialog(
                    context: context,
                    builder: (context) => const JoinRoomDialog(),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OptionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _OptionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: SamChatColors.accentSilent),
      title: Text(
        title,
        style: const TextStyle(color: SamChatColors.onSurface, fontSize: 16),
      ),
      subtitle: Text(
        subtitle,
        style:
            TextStyle(color: SamChatColors.onSurfaceDim, fontSize: 13),
      ),
      onTap: onTap,
    );
  }
}
