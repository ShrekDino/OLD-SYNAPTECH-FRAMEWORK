import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:matrix/matrix.dart';
import '../../auth/state/auth_notifier.dart';

class RoomService {
  static Future<void> startDirectChat(Client client, String userId) async {
    await client.startDirectChat(userId);
  }

  static Future<String> createGroup({
    required Client client,
    required String name,
    List<String> inviteUserIds = const [],
  }) async {
    final roomId = await client.createRoom(
      name: name,
      invite: inviteUserIds.toList(),
      preset: CreateRoomPreset.trustedPrivateChat,
    );
    return roomId;
  }

  static Future<void> joinRoom(Client client, String roomIdOrAlias) async {
    await client.joinRoom(roomIdOrAlias);
  }

  static Future<List<Profile>> searchUsers(
    Client client,
    String query,
  ) async {
    final result = await client.searchUserDirectory(query);
    return result.results;
  }
}

final userSearchProvider = FutureProvider.family<List<Profile>, String>(
  (ref, query) async {
    final authState = ref.watch(authNotifierProvider);
    final client = authState.client;
    if (client == null || query.trim().isEmpty) return [];
    return RoomService.searchUsers(client, query.trim());
  },
);
