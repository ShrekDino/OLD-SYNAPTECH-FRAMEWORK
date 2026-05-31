import '../../../core/models/notification_priority.dart';
import '../../stickers/models/sticker_pack.dart';
import '../models/chat_message.dart';

class ChatState {
  final String composingText;
  final NotificationPriority priority;
  final bool isSending;
  final bool showUrgentSentBadge;
  final List<ChatMessage> messages;
  final String? error;
  final bool isStickerKeyboardOpen;
  final List<MatrixImagePack> availablePacks;
  final bool isLoadingHistory;
  final bool hasMoreHistory;
  final bool isLoadingMore;

  const ChatState({
    this.composingText = '',
    this.priority = NotificationPriority.silent,
    this.isSending = false,
    this.showUrgentSentBadge = false,
    this.messages = const [],
    this.error,
    this.isStickerKeyboardOpen = false,
    this.availablePacks = const [],
    this.isLoadingHistory = false,
    this.hasMoreHistory = true,
    this.isLoadingMore = false,
  });

  ChatState copyWith({
    String? composingText,
    NotificationPriority? priority,
    bool? isSending,
    bool? showUrgentSentBadge,
    List<ChatMessage>? messages,
    String? error,
    bool? isStickerKeyboardOpen,
    List<MatrixImagePack>? availablePacks,
    bool? isLoadingHistory,
    bool? hasMoreHistory,
    bool? isLoadingMore,
    bool clearError = false,
  }) {
    return ChatState(
      composingText: composingText ?? this.composingText,
      priority: priority ?? this.priority,
      isSending: isSending ?? this.isSending,
      showUrgentSentBadge: showUrgentSentBadge ?? this.showUrgentSentBadge,
      messages: messages ?? this.messages,
      error: clearError ? null : (error ?? this.error),
      isStickerKeyboardOpen: isStickerKeyboardOpen ?? this.isStickerKeyboardOpen,
      availablePacks: availablePacks ?? this.availablePacks,
      isLoadingHistory: isLoadingHistory ?? this.isLoadingHistory,
      hasMoreHistory: hasMoreHistory ?? this.hasMoreHistory,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }
}
