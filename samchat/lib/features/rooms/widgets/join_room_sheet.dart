import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../auth/state/auth_notifier.dart';
import '../services/room_service.dart';

class JoinRoomDialog extends ConsumerStatefulWidget {
  const JoinRoomDialog({super.key});

  @override
  ConsumerState<JoinRoomDialog> createState() => _JoinRoomDialogState();
}

class _JoinRoomDialogState extends ConsumerState<JoinRoomDialog> {
  final _controller = TextEditingController();
  bool _isJoining = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _join() async {
    final roomIdOrAlias = _controller.text.trim();
    if (roomIdOrAlias.isEmpty) return;

    setState(() => _isJoining = true);

    try {
      final client = ref.read(authNotifierProvider).client;
      if (client == null) return;

      await RoomService.joinRoom(client, roomIdOrAlias);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to join: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isJoining = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: SamChatColors.surfaceElevated,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: const Text(
        'Join Room',
        style: TextStyle(color: SamChatColors.onSurface),
      ),
      content: TextField(
        controller: _controller,
        enabled: !_isJoining,
        style: const TextStyle(
          color: SamChatColors.onSurface,
          fontSize: 16,
        ),
        decoration: InputDecoration(
          hintText: '#room:server.org',
          hintStyle:
              TextStyle(color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5)),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: SamChatColors.inputBackground,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isJoining ? null : () => Navigator.of(context).pop(),
          child: Text(
            'Cancel',
            style: TextStyle(color: SamChatColors.onSurfaceDim),
          ),
        ),
        ElevatedButton(
          onPressed: _isJoining ? null : _join,
          style: ElevatedButton.styleFrom(
            backgroundColor: SamChatColors.accentSilent,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          child: _isJoining
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : const Text('Join'),
        ),
      ],
    );
  }
}
