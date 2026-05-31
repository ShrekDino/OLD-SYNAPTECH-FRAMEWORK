import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router.dart';
import 'core/design/app_theme.dart';
import 'features/settings/providers/settings_provider.dart';

class SamChatApp extends ConsumerWidget {
  const SamChatApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final settings = ref.watch(settingsProvider);
    final accent = settings.accentColor.color;

    return MaterialApp.router(
      key: ValueKey('${settings.accentColor.index}_${settings.themeMode.index}'),
      title: 'SamChat',
      debugShowCheckedModeBanner: false,
      theme: SamChatTheme.light(accent),
      darkTheme: SamChatTheme.dark(accent),
      themeMode: settings.themeMode,
      routerConfig: router,
    );
  }
}
