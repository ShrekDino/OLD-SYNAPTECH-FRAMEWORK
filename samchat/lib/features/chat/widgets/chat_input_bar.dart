import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../../core/models/notification_priority.dart';
import '../../../shared/widgets/urgent_indicator.dart';
import '../../auth/state/auth_notifier.dart';
import '../../stickers/widgets/sticker_picker_keyboard.dart';
import '../state/chat_notifier.dart';

class ChatInputBar extends ConsumerStatefulWidget {
  final String roomId;

  const ChatInputBar({super.key, required this.roomId});

  @override
  ConsumerState<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends ConsumerState<ChatInputBar>
    with SingleTickerProviderStateMixin {
  late final TextEditingController _textController;
  late final AnimationController _urgentPulseController;
  late final Animation<double> _urgentPulseAnimation;
  late final FocusNode _focusNode;

  bool _isUrgentMode = false;

  @override
  void initState() {
    super.initState();
    _textController = TextEditingController();
    _focusNode = FocusNode();

    _urgentPulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );

    _urgentPulseAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _urgentPulseController,
        curve: Curves.easeInOutSine,
      ),
    );

    _textController.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    _focusNode.dispose();
    _urgentPulseController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final notifier = ref.read(chatNotifierProvider(widget.roomId).notifier);
    notifier.onTextChanged(_textController.text);
  }

  void _onSendTap() {
    final notifier = ref.read(chatNotifierProvider(widget.roomId).notifier);
    final state = ref.read(chatNotifierProvider(widget.roomId));

    if (state.composingText.trim().isEmpty) return;

    notifier.send();
    _textController.clear();
    _exitUrgentMode();
  }

  void _onLongPressStart(LongPressStartDetails details) {
    final state = ref.read(chatNotifierProvider(widget.roomId));
    if (state.composingText.trim().isEmpty) return;

    HapticFeedback.heavyImpact();

    if (!_isUrgentMode) {
      _enterUrgentMode();
    } else {
      _exitUrgentMode();
    }
  }

  void _enterUrgentMode() {
    _isUrgentMode = true;
    ref.read(chatNotifierProvider(widget.roomId).notifier).setPriority(
          NotificationPriority.urgent,
        );
    _urgentPulseController.repeat(reverse: true);
    HapticFeedback.heavyImpact();
  }

  void _exitUrgentMode() {
    _isUrgentMode = false;
    ref.read(chatNotifierProvider(widget.roomId).notifier).setPriority(
          NotificationPriority.silent,
        );
    _urgentPulseController.stop();
    _urgentPulseController.reset();
  }

  void _onStickerToggle() {
    final notifier = ref.read(chatNotifierProvider(widget.roomId).notifier);
    notifier.toggleStickerKeyboard();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatNotifierProvider(widget.roomId));
    final hasText = chatState.composingText.trim().isNotEmpty;
    final homeserver = ref.watch(authNotifierProvider).homeserver ?? '';

    if (chatState.showUrgentSentBadge) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _showUrgentSentSnackbar();
        }
      });
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (chatState.isStickerKeyboardOpen)
          StickerPickerKeyboard(
            roomId: widget.roomId,
            homeserver: homeserver,
          ),
        Container(
          padding: EdgeInsets.only(
            left: 4,
            right: 8,
            top: 6,
            bottom: MediaQuery.of(context).padding.bottom + 6,
          ),
          decoration: const BoxDecoration(
            color: SamChatColors.surfaceElevated,
            border: Border(
              top: BorderSide(color: SamChatColors.divider, width: 0.5),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              _StickerToggleButton(
                isActive: chatState.isStickerKeyboardOpen,
                onTap: _onStickerToggle,
              ),
              const SizedBox(width: 2),
              Expanded(
                child: _UrgentInputField(
                  controller: _textController,
                  focusNode: _focusNode,
                  isUrgentMode: _isUrgentMode,
                  pulseAnimation: _urgentPulseAnimation,
                ),
              ),
              const SizedBox(width: 6),
              _SendButton(
                hasText: hasText,
                isUrgentMode: _isUrgentMode,
                onTap: hasText ? _onSendTap : null,
                onLongPressStart: _onLongPressStart,
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _showUrgentSentSnackbar() {
    final notifier = ref.read(chatNotifierProvider(widget.roomId).notifier);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            UrgentIndicator(size: 16),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                'Urgent message sent',
                style: TextStyle(
                  color: SamChatColors.onSurface,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        backgroundColor: SamChatColors.snackbarUrgent,
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(
            color: SamChatColors.accentUrgent,
            width: 1,
          ),
        ),
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 80),
      ),
    );
    notifier.dismissError();
  }
}

class _StickerToggleButton extends StatelessWidget {
  final bool isActive;
  final VoidCallback onTap;

  const _StickerToggleButton({
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 40,
        height: 40,
        margin: const EdgeInsets.only(bottom: 2),
        decoration: BoxDecoration(
          color: isActive
              ? SamChatColors.accentSilent.withValues(alpha: 0.15)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          isActive ? Icons.keyboard_rounded : Icons.emoji_emotions_outlined,
          color: isActive
              ? SamChatColors.accentSilent
              : SamChatColors.onSurfaceDim,
          size: 22,
        ),
      ),
    );
  }
}

class _UrgentInputField extends StatelessWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final bool isUrgentMode;
  final Animation<double> pulseAnimation;

  const _UrgentInputField({
    required this.controller,
    required this.focusNode,
    required this.isUrgentMode,
    required this.pulseAnimation,
  });

  @override
  Widget build(BuildContext context) {
    final inputWidget = Container(
      constraints: const BoxConstraints(maxHeight: 120),
      decoration: BoxDecoration(
        color: SamChatColors.inputBackground,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (isUrgentMode)
            Padding(
              padding: const EdgeInsets.only(left: 12, bottom: 10),
              child: UrgentIndicator(size: 16),
            ),
          Expanded(
            child: TextField(
              controller: controller,
              focusNode: focusNode,
              maxLines: null,
              textCapitalization: TextCapitalization.sentences,
              textInputAction: TextInputAction.newline,
              decoration: const InputDecoration(
                hintText: 'Message...',
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                isDense: true,
              ),
              style: const TextStyle(
                color: SamChatColors.onSurface,
                fontSize: 16,
                height: 1.35,
              ),
              cursorColor: isUrgentMode
                  ? SamChatColors.accentUrgent
                  : SamChatColors.accentSilent,
            ),
          ),
        ],
      ),
    );

    if (!isUrgentMode) return inputWidget;

    return ListenableBuilder(
      listenable: pulseAnimation,
      builder: (context, _) {
        final pulse = pulseAnimation.value;
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color:
                  SamChatColors.accentUrgent.withValues(alpha: 0.2 + pulse * 0.8),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: SamChatColors.accentUrgent
                    .withValues(alpha: 0.05 + pulse * 0.1),
                blurRadius: 8 + pulse * 6,
                spreadRadius: pulse,
              ),
            ],
          ),
          child: inputWidget,
        );
      },
    );
  }
}

class _SendButton extends StatelessWidget {
  final bool hasText;
  final bool isUrgentMode;
  final VoidCallback? onTap;
  final void Function(LongPressStartDetails) onLongPressStart;

  const _SendButton({
    required this.hasText,
    required this.isUrgentMode,
    required this.onTap,
    required this.onLongPressStart,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      onLongPressStart: onLongPressStart,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOutCubic,
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: hasText
              ? (isUrgentMode
                    ? SamChatColors.accentUrgent
                    : SamChatColors.accentSilent)
              : SamChatColors.onSurfaceDisabled,
          shape: BoxShape.circle,
          boxShadow: isUrgentMode && hasText
              ? [
                  BoxShadow(
                    color: SamChatColors.accentUrgent.withValues(alpha: 0.4),
                    blurRadius: 8,
                    spreadRadius: 1,
                  ),
                ]
              : null,
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 200),
          transitionBuilder: (child, animation) {
            return ScaleTransition(scale: animation, child: child);
          },
          child: isUrgentMode
              ? const Icon(
                  Icons.nearby_error_rounded,
                  key: ValueKey('urgent'),
                  color: Colors.white,
                  size: 22,
                )
              : const Icon(
                  Icons.arrow_upward_rounded,
                  key: ValueKey('silent'),
                  color: Colors.white,
                  size: 22,
                ),
        ),
      ),
    );
  }
}
