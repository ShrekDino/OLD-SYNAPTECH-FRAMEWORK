import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:matrix/matrix.dart';
import '../../../core/design/app_colors.dart';
import '../../auth/state/auth_notifier.dart';
import '../services/room_service.dart';

class UserSearchDelegate extends SearchDelegate<Profile?> {
  @override
  String get searchFieldLabel => 'Search Matrix users...';

  @override
  ThemeData appBarTheme(BuildContext context) {
    final theme = Theme.of(context);
    return theme.copyWith(
      inputDecorationTheme: const InputDecorationTheme(
        border: InputBorder.none,
        hintStyle: TextStyle(color: SamChatColors.onSurfaceDim),
      ),
    );
  }

  @override
  List<Widget>? buildActions(BuildContext context) {
    return [
      if (query.isNotEmpty)
        IconButton(
          icon: const Icon(Icons.clear),
          onPressed: () => query = '',
        ),
    ];
  }

  @override
  Widget? buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () => close(context, null),
    );
  }

  @override
  Widget buildResults(BuildContext context) => _buildSearchResults(context);

  @override
  Widget buildSuggestions(BuildContext context) => _buildSearchResults(context);

  Widget _buildSearchResults(BuildContext context) {
    if (query.trim().isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.search_rounded,
              size: 48,
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 12),
            Text(
              'Search for users by display name',
              style: TextStyle(
                color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                fontSize: 15,
              ),
            ),
          ],
        ),
      );
    }

    final client = ProviderScope.containerOf(context)
        .read(authNotifierProvider)
        .client;
    if (client == null) return const SizedBox();

    return FutureBuilder<List<Profile>>(
      future: RoomService.searchUsers(client, query.trim()),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError || !snapshot.hasData || snapshot.data!.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.person_search_outlined,
                  size: 48,
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                ),
                const SizedBox(height: 12),
                Text(
                  'No users found',
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                    fontSize: 15,
                  ),
                ),
              ],
            ),
          );
        }

        final profiles = snapshot.data!;
        return ListView.separated(
          itemCount: profiles.length,
          separatorBuilder: (context, index) => Divider(
            height: 0.5,
            color: SamChatColors.divider,
            indent: 76,
          ),
          itemBuilder: (context, index) {
            final profile = profiles[index];
            final displayName = profile.displayName ?? profile.userId;
            return _ProfileTile(
              displayName: displayName,
              userId: profile.userId,
              avatarUrl: profile.avatarUrl?.toString(),
              onTap: () async {
                try {
                  await RoomService.startDirectChat(client, profile.userId);
                  if (context.mounted) close(context, profile);
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Failed: $e')),
                    );
                  }
                }
              },
            );
          },
        );
      },
    );
  }
}

class _ProfileTile extends StatelessWidget {
  final String displayName;
  final String userId;
  final String? avatarUrl;
  final VoidCallback onTap;

  const _ProfileTile({
    required this.displayName,
    required this.userId,
    this.avatarUrl,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: SamChatColors.accentSilent,
        backgroundImage: avatarUrl != null ? NetworkImage(avatarUrl!) : null,
        child: avatarUrl == null
            ? Text(
                displayName.isNotEmpty ? displayName[0].toUpperCase() : '?',
                style: const TextStyle(color: Colors.white),
              )
            : null,
      ),
      title: Text(
        displayName,
        style: const TextStyle(color: SamChatColors.onSurface),
      ),
      subtitle: Text(
        userId,
        style: TextStyle(
          color: SamChatColors.onSurfaceDim,
          fontSize: 12,
        ),
      ),
      onTap: onTap,
    );
  }
}
