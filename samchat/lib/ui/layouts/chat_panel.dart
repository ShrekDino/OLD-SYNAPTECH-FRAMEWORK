import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/design/app_colors.dart';
import '../../features/auth/state/auth_notifier.dart';
import '../../features/chat/state/chat_notifier.dart';
import '../../features/chat/state/chat_state.dart';
import '../../features/chat/widgets/chat_input_bar.dart';
import '../views/chat/widgets/chat_bubble_group.dart' show groupMessages, ChatBubbleGroup;

class ChatPanel extends ConsumerStatefulWidget {
  final String roomId;

  const ChatPanel({super.key, required this.roomId});

  @override
  ConsumerState<ChatPanel> createState() => _ChatPanelState();
}

class _ChatPanelState extends ConsumerState<ChatPanel> {
  bool _readMarkerSent = false;
  bool _historyLoaded = false;
  final ScrollController _scrollController = ScrollController();
  static const double _scrollThreshold = 200.0;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _sendReadMarker();
    _loadInitialHistory();
  }

  void _loadInitialHistory() {
    if (_historyLoaded) return;
    _historyLoaded = true;
    Future.microtask(() {
      ref.read(chatNotifierProvider(widget.roomId).notifier).loadHistory();
    });
  }

  void _onScroll() {
    if (!_scrollController.hasClients) return;
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - _scrollThreshold) {
      ref.read(chatNotifierProvider(widget.roomId).notifier).loadHistory();
    }
  }

  void _sendReadMarker() {
    if (_readMarkerSent) return;
    _readMarkerSent = true;

    final authState = ref.read(authNotifierProvider);
    final client = authState.client;
    if (client == null) return;

    final room = client.getRoomById(widget.roomId);
    if (room == null) return;
    final lastEvent = room.lastEvent;
    if (lastEvent == null) return;

    room.setReadMarker(lastEvent.eventId).catchError((e) {
      debugPrint('[ChatPanel] setReadMarker error: $e');
    });
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatNotifierProvider(widget.roomId));
    final client = ref.watch(authNotifierProvider).client;
    final homeserver = client?.homeserver?.toString() ?? '';

    return Column(
      children: [
        Expanded(
          child: chatState.isLoadingHistory
              ? _buildLoadingState()
              : chatState.messages.isEmpty
                  ? _buildEmptyState()
                  : _buildMessageList(chatState, client?.userID ?? '', homeserver),
        ),
        ChatInputBar(roomId: widget.roomId),
      ],
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 32,
            height: 32,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              color: SamChatColors.accentSilent,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Loading messages...',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
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
            'No messages yet',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Messages you send appear here',
            style: TextStyle(
              color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageList(ChatState chatState, String userId, String homeserver) {
    final groups = groupMessages(chatState.messages);

    return ListView.builder(
      controller: _scrollController,
      reverse: true,
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: groups.length + (chatState.isLoadingMore ? 1 : 0),
      itemBuilder: (context, index) {
        if (chatState.isLoadingMore && index == groups.length) {
          return _buildLoadingMoreIndicator();
        }
        final group = groups[index];
        final isOwn = group.senderId == userId;
        return ChatBubbleGroup(
          group: group,
          isOwn: isOwn,
          homeserver: homeserver,
          isFirstGroup: index == 0,
        );
      },
    );
  }

  Widget _buildLoadingMoreIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
          ),
        ),
      ),
    );
  }
}
