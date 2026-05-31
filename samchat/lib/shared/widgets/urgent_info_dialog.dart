import 'package:flutter/material.dart';
import '../../core/design/app_colors.dart';

class UrgentInfoDialog extends StatefulWidget {
  final VoidCallback onDismiss;
  final bool isVisible;

  const UrgentInfoDialog({
    super.key,
    required this.onDismiss,
    this.isVisible = true,
  });

  @override
  State<UrgentInfoDialog> createState() => _UrgentInfoDialogState();
}

class _UrgentInfoDialogState extends State<UrgentInfoDialog>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fadeAnimation;
  late final Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeOut,
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeOutCubic,
      ),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _dismiss() {
    _controller.reverse().then((_) {
      widget.onDismiss();
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeAnimation.value,
          child: IgnorePointer(
            ignoring: _fadeAnimation.value < 0.01,
            child: child,
          ),
        );
      },
      child: GestureDetector(
        onTap: _dismiss,
        child: Container(
          color: SamChatColors.overlay,
          child: Center(
            child: GestureDetector(
              onTap: () {},
              child: Transform.scale(
                scale: _scaleAnimation.value,
                child: _buildCard(),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32),
      constraints: const BoxConstraints(maxWidth: 360),
      decoration: BoxDecoration(
        color: SamChatColors.surfaceElevated,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: SamChatColors.divider,
          width: 0.5,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.4),
            blurRadius: 32,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(height: 32),
          _buildIconRow(),
          const SizedBox(height: 20),
          _buildSection(
            icon: Icons.notifications_off_outlined,
            iconColor: SamChatColors.onSurfaceDim,
            title: 'Silent by Default',
            body: 'Messages arrive silently — no buzz, no sound, no interruption.',
          ),
          const SizedBox(height: 16),
          _buildDivider(),
          const SizedBox(height: 16),
          _buildSection(
            icon: Icons.nearby_error_rounded,
            iconColor: SamChatColors.accentUrgent,
            title: 'Urgent by Intent',
            body:
                'Long-press the send button to glow it red. Tap send — your alert pierces through silent mode and Do Not Disturb.\n\nUse urgency intentionally. It breaks through for a reason.',
          ),
          const SizedBox(height: 24),
          _buildGotItButton(),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildIconRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.notifications_off_outlined,
          size: 28,
          color: SamChatColors.onSurfaceDim.withValues(alpha: 0.5),
        ),
        const SizedBox(width: 8),
        Icon(
          Icons.remove,
          size: 20,
          color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
        ),
        const SizedBox(width: 8),
        Icon(
          Icons.nearby_error_rounded,
          size: 32,
          color: SamChatColors.accentUrgent,
        ),
      ],
    );
  }

  Widget _buildSection({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String body,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Icon(icon, size: 20, color: iconColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: SamChatColors.onSurface,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.2,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  body,
                  style: TextStyle(
                    color: SamChatColors.onSurfaceDim,
                    fontSize: 14,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Container(
        height: 1,
        color: SamChatColors.divider,
      ),
    );
  }

  Widget _buildGotItButton() {
    return SizedBox(
      width: double.infinity,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            gradient: const LinearGradient(
              colors: [
                SamChatColors.accentSilent,
                Color(0xFF0055CC),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: ElevatedButton(
            onPressed: _dismiss,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: const Text(
              'Got it',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
