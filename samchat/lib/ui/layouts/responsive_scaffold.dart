import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/design/app_colors.dart';
import '../../features/auth/state/auth_notifier.dart';
import '../../features/rooms/widgets/create_group_sheet.dart';
import '../../features/rooms/widgets/join_room_sheet.dart';
import '../../features/rooms/widgets/new_chat_fab.dart';
import '../../features/rooms/widgets/user_search_delegate.dart';
import '../providers/active_room_provider.dart';
import 'chat_panel.dart';
import 'room_list_panel.dart';

class ResponsiveScaffold extends ConsumerWidget {
  const ResponsiveScaffold({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;

        if (width >= 900) {
          return _DesktopScaffold();
        } else if (width >= 600) {
          return _TabletScaffold();
        } else {
          return _MobileScaffold();
        }
      },
    );
  }
}

class _MobileScaffold extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: SamChatColors.background,
      appBar: AppBar(
        title: const Text('SamChat'),
        actions: [
          _SettingsMenu(),
        ],
      ),
      body: RoomListPanel(),
      floatingActionButton: NewChatFab(),
    );
  }
}

class _TabletScaffold extends ConsumerStatefulWidget {
  @override
  ConsumerState<_TabletScaffold> createState() => _TabletScaffoldState();
}

class _TabletScaffoldState extends ConsumerState<_TabletScaffold> {
  @override
  Widget build(BuildContext context) {
    final activeRoomId = ref.watch(activeRoomIdProvider);

    return Scaffold(
      backgroundColor: SamChatColors.background,
      appBar: activeRoomId == null
          ? AppBar(
              title: const Text('SamChat'),
              actions: [const _SettingsMenu()],
            )
          : null,
      body: SafeArea(
        child: Row(
          children: [
            Expanded(
              flex: 1,
              child: activeRoomId != null
                  ? _buildRoomListWithBack()
                  : const RoomListPanel(),
            ),
            Container(
              width: 1,
              color: SamChatColors.divider,
            ),
            Expanded(
              flex: 1,
              child: activeRoomId != null
                  ? _buildChatView(activeRoomId)
                  : _buildEmptyChatSelection(),
            ),
          ],
        ),
      ),
      floatingActionButton: activeRoomId == null ? NewChatFab() : null,
    );
  }

  Widget _buildRoomListWithBack() {
    return Column(
      children: [
        Container(
          height: 56,
          padding: const EdgeInsets.symmetric(horizontal: 8),
          decoration: BoxDecoration(
            color: SamChatColors.surfaceElevated,
            border: Border(
              bottom: BorderSide(color: SamChatColors.divider, width: 0.5),
            ),
          ),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.chevron_left_rounded),
                onPressed: () {
                  ref.read(activeRoomIdProvider.notifier).state = null;
                },
              ),
              const SizedBox(width: 4),
              const Text(
                'SamChat',
                style: TextStyle(
                  color: SamChatColors.onSurface,
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: RoomListPanel(
            onRoomTap: (room) {
              ref.read(activeRoomIdProvider.notifier).state = room.id;
            },
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyChatSelection() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.chat_bubble_outline_rounded,
            size: 56,
            color: SamChatColors.onSurfaceDim.withValues(alpha: 0.2),
          ),
          const SizedBox(height: 16),
          Text(
            'Select a conversation',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
              fontSize: 18,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Choose a chat from the left panel',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatView(String roomId) {
    return Column(
      children: [
        _ChatHeader(
          roomId: roomId,
          onBack: () {
            ref.read(activeRoomIdProvider.notifier).state = null;
          },
        ),
        Expanded(
          child: ChatPanel(roomId: roomId),
        ),
      ],
    );
  }
}

class _DesktopScaffold extends ConsumerStatefulWidget {
  @override
  ConsumerState<_DesktopScaffold> createState() => _DesktopScaffoldState();
}

class _DesktopScaffoldState extends ConsumerState<_DesktopScaffold> {
  bool _navRailExpanded = false;

  @override
  Widget build(BuildContext context) {
    final activeRoomId = ref.watch(activeRoomIdProvider);

    return Scaffold(
      backgroundColor: SamChatColors.background,
      body: SafeArea(
        child: Row(
          children: [
            _AppNavigationRail(
              isExpanded: _navRailExpanded,
              onToggle: () {
                setState(() => _navRailExpanded = !_navRailExpanded);
              },
            ),
            Container(
              width: 1,
              color: SamChatColors.divider,
            ),
            SizedBox(
              width: _navRailExpanded ? 320 : 340,
              child: Column(
                children: [
                  _RoomListHeader(),
                  Expanded(
                    child: RoomListPanel(
                      onRoomTap: (room) {
                        ref.read(activeRoomIdProvider.notifier).state =
                            room.id;
                      },
                    ),
                  ),
                ],
              ),
            ),
            Container(
              width: 1,
              color: SamChatColors.divider,
            ),
            Expanded(
              child: activeRoomId != null
                  ? _buildChatView(activeRoomId)
                  : _buildEmptyChatSelection(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyChatSelection() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.chat_bubble_outline_rounded,
            size: 64,
            color: SamChatColors.onSurfaceDim.withValues(alpha: 0.15),
          ),
          const SizedBox(height: 20),
          Text(
            'Select a conversation',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.4),
              fontSize: 20,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Choose a chat from the left to start messaging',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.25),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatView(String roomId) {
    return Column(
      children: [
        _ChatHeader(roomId: roomId),
        Expanded(
          child: ChatPanel(roomId: roomId),
        ),
      ],
    );
  }
}

class _AppNavigationRail extends ConsumerWidget {
  final bool isExpanded;
  final VoidCallback onToggle;

  const _AppNavigationRail({
    required this.isExpanded,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final railWidth = isExpanded ? 200.0 : 68.0;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOutCubic,
      width: railWidth,
      color: SamChatColors.surfaceElevated,
      child: Column(
        children: [
          const SizedBox(height: 12),
          _NavRailTile(
            icon: Icons.chat_bubble_rounded,
            label: 'Chats',
            isExpanded: isExpanded,
            isSelected: true,
            onTap: () {},
          ),
          const Spacer(),
          _NavRailTile(
            icon: Icons.settings_outlined,
            label: 'Settings',
            isExpanded: isExpanded,
            isSelected: false,
            onTap: () {
              context.push('/settings');
            },
          ),
          const SizedBox(height: 4),
          _NavRailTile(
            icon: isExpanded
                ? Icons.chevron_left_rounded
                : Icons.chevron_right_rounded,
            label: 'Collapse',
            isExpanded: isExpanded,
            isSelected: false,
            onTap: onToggle,
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}

class _NavRailTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isExpanded;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavRailTile({
    required this.icon,
    required this.label,
    required this.isExpanded,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        padding: EdgeInsets.symmetric(
          horizontal: isExpanded ? 12 : 0,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          color: isSelected
              ? SamChatColors.accentSilent.withValues(alpha: 0.12)
              : null,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 44,
              child: Center(
                child: Icon(
                  icon,
                  size: 22,
                  color: isSelected
                      ? SamChatColors.accentSilent
                      : SamChatColors.onSurfaceDim,
                ),
              ),
            ),
            if (isExpanded) ...[
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  color: isSelected
                      ? SamChatColors.accentSilent
                      : SamChatColors.onSurfaceDim,
                  fontSize: 14,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _RoomListHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: SamChatColors.surfaceElevated,
        border: Border(
          bottom: BorderSide(color: SamChatColors.divider, width: 0.5),
        ),
      ),
      child: Row(
        children: [
          const Text(
            'SamChat',
            style: TextStyle(
              color: SamChatColors.onSurface,
              fontSize: 17,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.edit_rounded),
            color: SamChatColors.accentSilent,
            onPressed: () => _showCreateOptions(context),
          ),
        ],
      ),
    );
  }

  void _showCreateOptions(BuildContext context) {
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
        style: TextStyle(color: SamChatColors.onSurfaceDim, fontSize: 13),
      ),
      onTap: onTap,
    );
  }
}

class _ChatHeader extends ConsumerWidget {
  final String roomId;
  final VoidCallback? onBack;

  const _ChatHeader({
    required this.roomId,
    this.onBack,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final client = ref.watch(authNotifierProvider).client;
    final room = client?.getRoomById(roomId);
    final displayName = room?.getLocalizedDisplayname() ?? roomId;

    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      decoration: BoxDecoration(
        color: SamChatColors.surfaceElevated,
        border: Border(
          bottom: BorderSide(color: SamChatColors.divider, width: 0.5),
        ),
      ),
      child: Row(
        children: [
          if (onBack != null)
            IconButton(
              icon: const Icon(Icons.chevron_left_rounded),
              onPressed: onBack,
            ),
          if (onBack == null) const SizedBox(width: 8),
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: SamChatColors.accentSilent.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                displayName.isNotEmpty ? displayName[0].toUpperCase() : '?',
                style: TextStyle(
                  color: SamChatColors.accentSilent,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              displayName,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: SamChatColors.onSurface,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsMenu extends ConsumerWidget {
  const _SettingsMenu();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PopupMenuButton<String>(
      icon: const Icon(Icons.settings_outlined),
      onSelected: (value) async {
        if (value == 'settings') {
          context.push('/settings');
        } else if (value == 'logout') {
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
            ref.read(authNotifierProvider.notifier).logout();
          }
        }
      },
      itemBuilder: (context) => [
        const PopupMenuItem(
          value: 'settings',
          child: Row(
            children: [
              Icon(Icons.tune_rounded, size: 18),
              SizedBox(width: 10),
              Text('Settings'),
            ],
          ),
        ),
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
    );
  }
}
