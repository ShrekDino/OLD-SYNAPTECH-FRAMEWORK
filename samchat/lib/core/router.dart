import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../features/auth/state/auth_notifier.dart';
import '../features/chat/widgets/chat_screen.dart';
import '../features/settings/widgets/settings_screen.dart';
import '../ui/layouts/responsive_scaffold.dart';
import '../ui/views/login/homeserver_picker_view.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/rooms',
    redirect: (context, state) {
      final isLoggedIn = authState.status == AuthStatus.loggedIn;
      final isLoginRoute = state.matchedLocation == '/login';

      if (authState.status == AuthStatus.unknown ||
          authState.status == AuthStatus.restoring) {
        return null;
      }

      if (!isLoggedIn && !isLoginRoute) return '/login';
      if (isLoggedIn && isLoginRoute) return '/rooms';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const HomeserverPickerView(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/rooms',
        builder: (context, state) => const ResponsiveScaffold(),
        routes: [
          GoRoute(
            path: ':roomId/chat',
            builder: (context, state) {
              final roomId = state.pathParameters['roomId']!;
              return ChatScreen(
                roomId: roomId,
                roomName: state.extra as String? ?? roomId,
              );
            },
          ),
        ],
      ),
    ],
  );
});
