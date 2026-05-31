import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/design/app_colors.dart';
import '../../auth/state/auth_notifier.dart';
import '../models/app_settings.dart';
import '../providers/settings_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: SamChatColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.chevron_left_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          _AppearanceSection(),
          const _SectionDivider(),
          _NotificationsSection(),
          const _SectionDivider(),
          _PrivacySection(),
          const _SectionDivider(),
          _ChatSection(),
          const _SectionDivider(),
          _AboutSection(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

class _SectionDivider extends StatelessWidget {
  const _SectionDivider();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
      child: Container(height: 1, color: SamChatColors.divider),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;

  const _SectionHeader({required this.title, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: SamChatColors.onSurfaceDim),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              color: SamChatColors.onSurfaceDim,
              fontSize: 13,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: SamChatColors.accentSilent, size: 22),
      title: Text(
        title,
        style: const TextStyle(
          color: SamChatColors.onSurface,
          fontSize: 16,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle!,
              style: TextStyle(
                color: SamChatColors.onSurfaceDim,
                fontSize: 13,
              ),
            )
          : null,
      trailing: trailing ?? (onTap != null
          ? Icon(Icons.chevron_right_rounded,
              color: SamChatColors.onSurfaceDim, size: 20)
          : null),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20),
    );
  }
}

class _AppearanceSection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: 'APPEARANCE', icon: Icons.palette_outlined),
        _SettingsTile(
          icon: Icons.brightness_6_outlined,
          title: 'Theme',
          subtitle: _themeLabel(settings.themeMode),
          onTap: () => _showThemePicker(context, ref, settings, notifier),
        ),
        _SettingsTile(
          icon: Icons.color_lens_outlined,
          title: 'Accent color',
          subtitle: settings.accentColor.label,
          trailing: Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: settings.accentColor.color,
              shape: BoxShape.circle,
              border: Border.all(
                color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                width: 1,
              ),
            ),
          ),
          onTap: () => _showColorPicker(context, ref, settings, notifier),
        ),
        _SettingsTile(
          icon: Icons.chat_bubble_outline_rounded,
          title: 'Bubble style',
          subtitle: settings.bubbleStyle.label,
          onTap: () => _showBubbleStylePicker(context, ref, settings, notifier),
        ),
      ],
    );
  }

  String _themeLabel(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.dark:
        return 'Dark';
      case ThemeMode.light:
        return 'Light';
      case ThemeMode.system:
        return 'System default';
    }
  }

  void _showThemePicker(BuildContext context, WidgetRef ref,
      AppSettings settings, SettingsNotifier notifier) {
    showModalBottomSheet(
      context: context,
      backgroundColor: SamChatColors.surfaceElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Text(
                'Theme',
                style: TextStyle(
                  color: SamChatColors.onSurface,
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              _themeOption(ctx, ThemeMode.dark, 'Dark', settings, notifier),
              _themeOption(ctx, ThemeMode.light, 'Light', settings, notifier),
              _themeOption(
                  ctx, ThemeMode.system, 'System default', settings, notifier),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }

  Widget _themeOption(BuildContext context, ThemeMode mode, String label,
      AppSettings current, SettingsNotifier notifier) {
    final isSelected = current.themeMode == mode;
    return ListTile(
      leading: Icon(
        mode == ThemeMode.dark
            ? Icons.dark_mode_rounded
            : mode == ThemeMode.light
                ? Icons.light_mode_rounded
                : Icons.settings_brightness_rounded,
        color: isSelected
            ? SamChatColors.accentSilent
            : SamChatColors.onSurfaceDim,
      ),
      title: Text(
        label,
        style: TextStyle(
          color: SamChatColors.onSurface,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
        ),
      ),
      trailing: isSelected
          ? Icon(Icons.check_rounded,
              color: SamChatColors.accentSilent, size: 22)
          : null,
      onTap: () {
        notifier.setThemeMode(mode);
        Navigator.pop(context);
      },
    );
  }

  void _showColorPicker(BuildContext context, WidgetRef ref,
      AppSettings settings, SettingsNotifier notifier) {
    showModalBottomSheet(
      context: context,
      backgroundColor: SamChatColors.surfaceElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Text(
                'Accent Color',
                style: TextStyle(
                  color: SamChatColors.onSurface,
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 16,
                runSpacing: 16,
                alignment: WrapAlignment.center,
                children: AccentColorOption.values.map((option) {
                  final isSelected = settings.accentColor == option;
                  return GestureDetector(
                    onTap: () {
                      notifier.setAccentColor(option);
                      Navigator.pop(context);
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: option.color,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: isSelected
                              ? Colors.white
                              : SamChatColors.onSurfaceDim
                                  .withValues(alpha: 0.2),
                          width: isSelected ? 3 : 1,
                        ),
                        boxShadow: isSelected
                            ? [
                                BoxShadow(
                                  color: option.color.withValues(alpha: 0.4),
                                  blurRadius: 12,
                                  spreadRadius: 2,
                                ),
                              ]
                            : null,
                      ),
                      child: isSelected
                          ? const Icon(Icons.check_rounded,
                              color: Colors.white, size: 24)
                          : null,
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  void _showBubbleStylePicker(BuildContext context, WidgetRef ref,
      AppSettings settings, SettingsNotifier notifier) {
    showModalBottomSheet(
      context: context,
      backgroundColor: SamChatColors.surfaceElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: SamChatColors.onSurfaceDim.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Text(
                'Bubble Style',
                style: TextStyle(
                  color: SamChatColors.onSurface,
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              ...ChatBubbleStyle.values.map((style) {
                final isSelected = settings.bubbleStyle == style;
                return ListTile(
                  leading: Icon(
                    Icons.rounded_corner_rounded,
                    color: isSelected
                        ? SamChatColors.accentSilent
                        : SamChatColors.onSurfaceDim,
                  ),
                  title: Text(
                    style.label,
                    style: TextStyle(
                      color: SamChatColors.onSurface,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    ),
                  ),
                  trailing: isSelected
                      ? Icon(Icons.check_rounded,
                          color: SamChatColors.accentSilent, size: 22)
                      : null,
                  onTap: () {
                    notifier.setBubbleStyle(style);
                    Navigator.pop(context);
                  },
                );
              }),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}

class _NotificationsSection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(
            title: 'NOTIFICATIONS', icon: Icons.notifications_outlined),
        _SettingsTile(
          icon: Icons.warning_amber_rounded,
          title: 'Urgent message sound',
          subtitle: settings.urgentNotificationSound ? 'Enabled' : 'Disabled',
          trailing: Switch.adaptive(
            value: settings.urgentNotificationSound,
            activeColor: SamChatColors.accentSilent,
            onChanged: notifier.setUrgentNotificationSound,
          ),
          onTap: () =>
              notifier.setUrgentNotificationSound(!settings.urgentNotificationSound),
        ),
        _SettingsTile(
          icon: Icons.vibration_outlined,
          title: 'Silent message vibration',
          subtitle: settings.silentNotificationVibration ? 'Enabled' : 'Disabled',
          trailing: Switch.adaptive(
            value: settings.silentNotificationVibration,
            activeColor: SamChatColors.accentSilent,
            onChanged: notifier.setSilentNotificationVibration,
          ),
          onTap: () => notifier
              .setSilentNotificationVibration(!settings.silentNotificationVibration),
        ),
      ],
    );
  }
}

class _PrivacySection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: 'PRIVACY', icon: Icons.lock_outlined),
        _SettingsTile(
          icon: Icons.done_all_rounded,
          title: 'Read receipts',
          subtitle: settings.showReadReceipts ? 'Visible to others' : 'Hidden',
          trailing: Switch.adaptive(
            value: settings.showReadReceipts,
            activeColor: SamChatColors.accentSilent,
            onChanged: notifier.setShowReadReceipts,
          ),
          onTap: () =>
              notifier.setShowReadReceipts(!settings.showReadReceipts),
        ),
        _SettingsTile(
          icon: Icons.keyboard_outlined,
          title: 'Typing indicators',
          subtitle:
              settings.showTypingIndicators ? 'Visible to others' : 'Hidden',
          trailing: Switch.adaptive(
            value: settings.showTypingIndicators,
            activeColor: SamChatColors.accentSilent,
            onChanged: notifier.setShowTypingIndicators,
          ),
          onTap: () => notifier
              .setShowTypingIndicators(!settings.showTypingIndicators),
        ),
      ],
    );
  }
}

class _ChatSection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: 'CHAT', icon: Icons.chat_outlined),
        _SettingsTile(
          icon: Icons.text_fields_rounded,
          title: 'Font size',
          subtitle: '${settings.fontSize.toInt()}pt',
          trailing: SizedBox(
            width: 120,
            child: Slider(
              value: settings.fontSize,
              min: 12.0,
              max: 24.0,
              divisions: 12,
              activeColor: SamChatColors.accentSilent,
              inactiveColor: SamChatColors.onSurfaceDisabled,
              label: '${settings.fontSize.toInt()}pt',
              onChanged: notifier.setFontSize,
            ),
          ),
        ),
        _SettingsTile(
          icon: Icons.keyboard_return_outlined,
          title: 'Enter to send',
          subtitle: settings.enterToSend ? 'Enabled' : 'Disabled',
          trailing: Switch.adaptive(
            value: settings.enterToSend,
            activeColor: SamChatColors.accentSilent,
            onChanged: notifier.setEnterToSend,
          ),
          onTap: () => notifier.setEnterToSend(!settings.enterToSend),
        ),
      ],
    );
  }
}

class _AboutSection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeader(title: 'ABOUT', icon: Icons.info_outline_rounded),
        const _SettingsTile(
          icon: Icons.tag_rounded,
          title: 'Version',
          subtitle: '0.6.0',
        ),
        _SettingsTile(
          icon: Icons.code_rounded,
          title: 'Open source licenses',
          subtitle: 'View licenses',
          onTap: () => showLicensePage(
            context: context,
            applicationName: 'SamChat',
            applicationVersion: '0.6.2',
            applicationIcon: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: SamChatColors.accentSilent.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Text(
                  'SC',
                  style: TextStyle(
                    color: SamChatColors.accentSilent,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            applicationLegalese: '\u00a9 2026 SamChat Contributors',
          ),
        ),
        _SettingsTile(
          icon: Icons.logout_rounded,
          title: 'Log out',
          subtitle: 'Sign out of your account',
          trailing: Icon(Icons.chevron_right_rounded,
              color: SamChatColors.accentUrgent, size: 20),
          onTap: () async {
            final confirmed = await showDialog<bool>(
              context: context,
              builder: (ctx) => AlertDialog(
                backgroundColor: SamChatColors.surfaceElevated,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                title: const Text('Log out',
                    style: TextStyle(color: SamChatColors.onSurface)),
                content: const Text('Are you sure you want to log out?',
                    style: TextStyle(color: SamChatColors.onSurfaceDim)),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.of(ctx).pop(false),
                    child: const Text('Cancel'),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(ctx).pop(true),
                    child: Text('Log out',
                        style:
                            TextStyle(color: SamChatColors.accentUrgent)),
                  ),
                ],
              ),
            );
            if (confirmed == true && context.mounted) {
              ref.read(authNotifierProvider.notifier).logout();
            }
          },
        ),
      ],
    );
  }
}
