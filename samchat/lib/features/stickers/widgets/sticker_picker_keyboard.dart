import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../chat/state/chat_notifier.dart';
import '../models/sticker_pack.dart';

String _mxcToHttp(String mxcUrl, String homeserver) {
  if (!mxcUrl.startsWith('mxc://')) return mxcUrl;
  final stripped = mxcUrl.replaceFirst('mxc://', '');
  final parts = stripped.split('/');
  if (parts.length < 2) return mxcUrl;
  return '$homeserver/_matrix/media/v3/download/${parts[0]}/${parts[1]}';
}

class StickerPickerKeyboard extends ConsumerStatefulWidget {
  final String roomId;
  final String homeserver;

  const StickerPickerKeyboard({
    super.key,
    required this.roomId,
    required this.homeserver,
  });

  @override
  ConsumerState<StickerPickerKeyboard> createState() =>
      _StickerPickerKeyboardState();
}

class _StickerPickerKeyboardState
    extends ConsumerState<StickerPickerKeyboard> {
  int _activePackIndex = 0;

  void _onStickerTap(PackImage image, String shortcode) {
    HapticFeedback.lightImpact();
    final notifier = ref.read(chatNotifierProvider(widget.roomId).notifier);
    notifier.sendSticker(
      mxcUrl: image.url,
      body: image.body ?? shortcode,
      info: image.info ?? {},
    );
    notifier.toggleStickerKeyboard();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatNotifierProvider(widget.roomId));
    final packs = chatState.availablePacks;

    if (packs.isEmpty) {
      return Container(
        height: 240,
        color: SamChatColors.surfaceElevated,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.emoji_emotions_outlined,
                size: 40,
                color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
              ),
              const SizedBox(height: 8),
              Text(
                'No sticker packs in this room',
                style: TextStyle(
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      );
    }

    _activePackIndex =
        _activePackIndex.clamp(0, packs.length - 1);
    final activePack = packs[_activePackIndex];

    return Container(
      height: 280,
      color: SamChatColors.surfaceElevated,
      child: Column(
        children: [
          Expanded(
            child: _buildStickerGrid(activePack),
          ),
          _buildPackTabs(packs),
        ],
      ),
    );
  }

  Widget _buildStickerGrid(MatrixImagePack pack) {
    final images = pack.images.entries.toList();

    if (images.isEmpty) {
      return Center(
        child: Text(
          'No stickers in this pack',
          style: TextStyle(
            color: SamChatColors.onSurfaceDim.withValues(alpha: 0.4),
            fontSize: 13,
          ),
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 4),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        childAspectRatio: 1,
        crossAxisSpacing: 4,
        mainAxisSpacing: 4,
      ),
      itemCount: images.length,
      itemBuilder: (context, index) {
        final entry = images[index];
        final shortcode = entry.key;
        final image = entry.value;

        return GestureDetector(
          onTap: () => _onStickerTap(image, shortcode),
          child: Container(
            decoration: BoxDecoration(
              color: SamChatColors.surface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: SamChatColors.divider,
                width: 0.5,
              ),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                _mxcToHttp(image.url, widget.homeserver),
                fit: BoxFit.contain,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  final total = loadingProgress.expectedTotalBytes;
                  final progress = total != null
                      ? loadingProgress.cumulativeBytesLoaded / total
                      : null;
                  return Center(
                    child: CircularProgressIndicator(
                      value: progress,
                      strokeWidth: 2,
                      color: SamChatColors.accentSilent,
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Icon(
                    Icons.broken_image_outlined,
                    color: SamChatColors.onSurfaceDim.withValues(alpha: 0.4),
                    size: 24,
                  );
                },
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPackTabs(List<MatrixImagePack> packs) {
    return Container(
      height: 48,
      decoration: BoxDecoration(
        color: SamChatColors.surface,
        border: Border(
          top: BorderSide(color: SamChatColors.divider, width: 0.5),
        ),
      ),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        itemCount: packs.length,
        itemBuilder: (context, index) {
          final pack = packs[index];
          final isActive = index == _activePackIndex;

          return GestureDetector(
            onTap: () => setState(() => _activePackIndex = index),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 6),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(
                    color: isActive
                        ? SamChatColors.accentSilent
                        : Colors.transparent,
                    width: 2.5,
                  ),
                ),
              ),
              child: _buildPackIcon(pack),
            ),
          );
        },
      ),
    );
  }

  Widget _buildPackIcon(MatrixImagePack pack) {
    final avatarUrl = pack.avatarUrl;

    if (avatarUrl != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(6),
        child: Image.network(
          _mxcToHttp(avatarUrl, widget.homeserver),
          width: 28,
          height: 28,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildFallbackPackIcon(pack);
          },
        ),
      );
    }

    return _buildFallbackPackIcon(pack);
  }

  Widget _buildFallbackPackIcon(MatrixImagePack pack) {
    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        color: SamChatColors.surfaceElevated,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Icon(
        Icons.emoji_emotions_rounded,
        size: 18,
        color: SamChatColors.onSurfaceDim,
      ),
    );
  }
}
