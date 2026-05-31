import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/sticker_pack.dart';

class StickerService {
  static Future<List<MatrixImagePack>> getPacks({
    required String roomId,
    required String homeserver,
    required String accessToken,
  }) async {
    final uri = Uri.parse(
      '$homeserver/_matrix/client/v3/rooms/$roomId/state/m.room.image_pack',
    );

    try {
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode != 200) return [];
      final body = response.body;
      if (body.isEmpty || body == '{}') return [];

      final parsed = jsonDecode(body);
      if (parsed is! List) return [];

      final packs = <MatrixImagePack>[];
      for (final entry in parsed) {
        if (entry is! Map<String, dynamic>) continue;
        final content = entry['content'] as Map<String, dynamic>? ?? {};
        final stateKey = entry['state_key'] as String? ?? '';
        packs.add(MatrixImagePack.fromStateEvent(
          packId: stateKey,
          roomId: roomId,
          content: content,
        ));
      }

      return packs.where((p) => p.isStickerPack).toList();
    } catch (e) {
      print('StickerService.getPacks error: $e');
      return [];
    }
  }
}
