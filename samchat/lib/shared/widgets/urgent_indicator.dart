import 'package:flutter/material.dart';
import '../../core/design/app_colors.dart';

class UrgentIndicator extends StatelessWidget {
  final double size;
  final Color? color;

  const UrgentIndicator({
    super.key,
    this.size = 16,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Icon(
      Icons.nearby_error_rounded,
      size: size,
      color: color ?? SamChatColors.accentUrgent,
    );
  }
}

class UrgentBadge extends StatelessWidget {
  final double size;

  const UrgentBadge({super.key, this.size = 8});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        color: SamChatColors.accentUrgent,
        shape: BoxShape.circle,
      ),
    );
  }
}
