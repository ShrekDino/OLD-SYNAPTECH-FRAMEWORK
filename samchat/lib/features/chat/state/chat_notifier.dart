import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:http/http.dart' as http;
import 'package:matrix/matrix.dart';
import '../../../core/models/notification_priority.dart';
import '../../auth/state/auth_notifier.dart';
import '../../stickers/models/sticker_message.dart';
import '../../stickers/services/sticker_service.dart';
import '../models/chat_message.dart';
import 'chat_state.dart';

const _uuid = Uuid();

class ChatNotifier extends StateNotifier<ChatState> {
  final String _roomId;
  final Client _client;
  bool _disposed = false;
  StreamSubscription<EventUpdate>? _eventSub;
  bool _loadingHistory = false;

  ChatNotifier({
    required String roomId,
    required Client client,
  })  : _roomId = roomId,
        _client = client,
        super(const ChatState()) {
    _setupEventSubscription();
    Future.microtask(_loadInitialHistory);
  }

  void _setupEventSubscription() {
    _eventSub = _client.onEvent.stream.listen(
      (update) {
        if (_disposed) return;
        if (update.roomID != _roomId) return;
        if (update.type != EventUpdateType.timeline &&
            update.type != EventUpdateType.history) {
          return;
        }

        final content = update.content;
        final eventType = content['type'] as String?;
        if (eventType != 'm.room.message' && eventType != 'm.sticker') return;

        final eventContent = content['content'] as Map<String, dynamic>? ?? {};
        final sender = content['sender'] as String? ?? '';
        final eventId = content['event_id'] as String? ?? '';
        final body = eventContent['body'] as String? ?? '';
        final isUrgent = eventContent['org.custom.urgency'] == 'urgent';
        final tsMs = content['origin_server_ts'] as int?;

        if (update.type == EventUpdateType.timeline && sender == _client.userID) return;

        addRemoteMessage(ChatMessage(
          id: eventId,
          roomId: _roomId,
          senderId: sender,
          body: body,
          priority: isUrgent ? NotificationPriority.urgent : NotificationPriority.silent,
          timestamp: tsMs != null
              ? DateTime.fromMillisecondsSinceEpoch(tsMs)
              : DateTime.now(),
          isSent: true,
          isRemote: true,
          eventType: eventType,
          stickerUrl: eventType == 'm.sticker' ? eventContent['url'] as String? : null,
        ));
      },
      onError: (e) {
        debugPrint('[ChatNotifier] onEvent error: $e');
      },
    );
  }

  Future<void> _loadInitialHistory() async {
    if (_disposed) return;
    await loadHistory();
  }

  Future<void> loadHistory() async {
    if (_disposed) return;
    if (_loadingHistory) return;
    if (!state.hasMoreHistory && state.messages.isNotEmpty) return;

    final room = _client.getRoomById(_roomId);
    if (room == null) return;

    _loadingHistory = true;

    final isInitial = state.messages.isEmpty;

    state = state.copyWith(
      isLoadingHistory: isInitial,
      isLoadingMore: !isInitial,
    );

    try {
      final count = await room.requestHistory(historyCount: 50);
      if (!_disposed) {
        state = state.copyWith(
          isLoadingHistory: false,
          isLoadingMore: false,
          hasMoreHistory: room.prev_batch != null && count >= 50,
        );
      }
    } catch (e) {
      if (!_disposed) {
        state = state.copyWith(
          isLoadingHistory: false,
          isLoadingMore: false,
          error: 'Failed to load history: $e',
        );
      }
    } finally {
      _loadingHistory = false;
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _eventSub?.cancel();
    super.dispose();
  }

  void onTextChanged(String text) {
    state = state.copyWith(composingText: text);
  }

  void togglePriority() {
    state = state.copyWith(priority: state.priority.toggle());
  }

  void setPriority(NotificationPriority priority) {
    state = state.copyWith(priority: priority);
  }

  void addRemoteMessage(ChatMessage message) {
    final updated = [message, ...state.messages];
    final seen = <String>{};
    final deduped = <ChatMessage>[];
    for (final m in updated) {
      if (seen.add(m.id)) deduped.add(m);
    }
    deduped.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    state = state.copyWith(messages: deduped);
  }

  void toggleStickerKeyboard() {
    final opening = !state.isStickerKeyboardOpen;
    state = state.copyWith(isStickerKeyboardOpen: opening);
    if (opening) fetchStickerPacks();
  }

  void closeStickerKeyboard() {
    if (state.isStickerKeyboardOpen) {
      state = state.copyWith(isStickerKeyboardOpen: false);
    }
  }

  Future<void> fetchStickerPacks() async {
    final packs = await StickerService.getPacks(
      roomId: _roomId,
      homeserver: _client.homeserver?.toString() ?? '',
      accessToken: _client.accessToken ?? '',
    );
    if (!_disposed) {
      state = state.copyWith(availablePacks: packs);
    }
  }

  String get _homeserver => _client.homeserver?.toString() ?? '';
  String get _accessToken => _client.accessToken ?? '';

  Future<void> send() async {
    final text = state.composingText.trim();
    if (text.isEmpty) return;

    final wasUrgent = state.priority.isUrgent;

    state = state.copyWith(isSending: true);

    final messageId = _uuid.v4();
    final localMessage = ChatMessage(
      id: messageId,
      roomId: _roomId,
      senderId: _client.userID ?? '',
      body: text,
      priority: state.priority,
      timestamp: DateTime.now(),
      isSent: false,
      isRemote: false,
    );

    state = state.copyWith(
      messages: [localMessage, ...state.messages],
      composingText: '',
      isSending: false,
      priority: NotificationPriority.silent,
      showUrgentSentBadge: wasUrgent,
    );

    _sendRequest(
      messageId: messageId,
      eventType: 'm.room.message',
      content: {
        'msgtype': 'm.text',
        'body': text,
        if (wasUrgent) 'org.custom.urgency': 'urgent',
      },
      wasUrgent: wasUrgent,
    );
  }

  Future<void> sendSticker({
    required String mxcUrl,
    required String body,
    required Map<String, dynamic> info,
  }) async {
    final wasUrgent = state.priority.isUrgent;

    final messageId = _uuid.v4();
    final localMessage = ChatMessage(
      id: messageId,
      roomId: _roomId,
      senderId: _client.userID ?? '',
      body: body,
      priority: state.priority,
      timestamp: DateTime.now(),
      isSent: false,
      isRemote: false,
      eventType: 'm.sticker',
      stickerUrl: mxcUrl,
    );

    state = state.copyWith(
      messages: [localMessage, ...state.messages],
      priority: NotificationPriority.silent,
      showUrgentSentBadge: wasUrgent,
    );

    final stickerContent = StickerMessageContent(
      body: body,
      url: mxcUrl,
      info: info,
      priority: wasUrgent ? NotificationPriority.urgent : NotificationPriority.silent,
    );

    _sendRequest(
      messageId: messageId,
      eventType: 'm.sticker',
      content: stickerContent.toJson(),
      wasUrgent: wasUrgent,
    );
  }

  Future<void> _sendRequest({
    required String messageId,
    required String eventType,
    required Map<String, dynamic> content,
    required bool wasUrgent,
  }) async {
    try {
      final eventBody = jsonEncode({
        'type': eventType,
        'content': content,
      });

      final sendUri = Uri.parse(
        '$_homeserver/_matrix/client/v3/rooms/$_roomId/send/$eventType/$messageId',
      );

      final response = await http.put(
        sendUri,
        headers: {
          'Authorization': 'Bearer $_accessToken',
          'Content-Type': 'application/json',
        },
        body: eventBody,
      );

      final messageIndex = state.messages.indexWhere((m) => m.id == messageId);
      if (messageIndex < 0) return;

      final updatedMessages = [...state.messages];

      if (response.statusCode == 200) {
        final eventId =
            (jsonDecode(response.body) as Map<String, dynamic>)['event_id']
                as String;
        updatedMessages[messageIndex] =
            updatedMessages[messageIndex].copyWith(
          isSent: true,
          id: eventId,
          isRemote: true,
        );
        state = state.copyWith(messages: updatedMessages);
      } else {
        updatedMessages[messageIndex] =
            updatedMessages[messageIndex].copyWith(isSent: false);
        state = state.copyWith(
          messages: updatedMessages,
          error: 'Failed to send (${response.statusCode})',
        );
      }
    } catch (e) {
      final messageIndex = state.messages.indexWhere((m) => m.id == messageId);
      if (messageIndex >= 0) {
        final updatedMessages = [...state.messages];
        updatedMessages[messageIndex] =
            updatedMessages[messageIndex].copyWith(isSent: false);
        state = state.copyWith(messages: updatedMessages, error: e.toString());
      }
    }

    if (wasUrgent) {
      Future.delayed(const Duration(seconds: 3), () {
        if (!_disposed) {
          state = state.copyWith(showUrgentSentBadge: false);
        }
      });
    }
  }

  void dismissError() {
    state = state.copyWith(error: null);
  }
}

final chatNotifierProvider =
    StateNotifierProvider.family<ChatNotifier, ChatState, String>(
  (ref, roomId) {
    final authState = ref.watch(authNotifierProvider);
    final client = authState.client;
    if (client == null) throw Exception('Cannot create ChatNotifier: no Matrix client');
    return ChatNotifier(
      roomId: roomId,
      client: client,
    );
  },
);
