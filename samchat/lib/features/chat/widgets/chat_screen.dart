import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../../ui/layouts/chat_panel.dart';

class ChatScreen extends ConsumerWidget {
  final String roomId;
  final String roomName;

  const ChatScreen({
    super.key,
    required this.roomId,
    this.roomName = '',
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: SamChatColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.chevron_left_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Flexible(
              child: Text(
                roomName.isNotEmpty ? roomName : roomId,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: ChatPanel(roomId: roomId),
      ),
    );
  }
}
