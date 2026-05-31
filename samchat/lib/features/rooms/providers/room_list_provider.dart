import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:matrix/matrix.dart';
import '../../auth/state/auth_notifier.dart';

final roomListProvider = StreamProvider<List<Room>>((ref) {
  final authState = ref.watch(authNotifierProvider);
  final client = authState.client;

  if (client == null) return const Stream.empty();

  final controller = StreamController<List<Room>>.broadcast();

  void emit() {
    if (controller.isClosed) return;
    try {
      final rooms = client.rooms.toList();
      rooms.sort((a, b) {
        final aTime = a.lastEvent?.originServerTs.millisecondsSinceEpoch ?? 0;
        final bTime = b.lastEvent?.originServerTs.millisecondsSinceEpoch ?? 0;
        return (bTime - aTime).sign;
      });
      controller.add(rooms);
    } catch (e, s) {
      debugPrint('[roomListProvider] emit error: $e\n$s');
    }
  }

  emit();

  final syncSub = client.onSync.stream.listen(
    (_) => emit(),
    onError: (e) {
      debugPrint('[roomListProvider] sync error: $e');
      emit();
    },
  );

  ref.onDispose(() {
    syncSub.cancel();
    controller.close();
  });

  return controller.stream;
});

final roomListLoadingProvider = Provider<bool>((ref) {
  final authState = ref.watch(authNotifierProvider);
  return authState.status == AuthStatus.unknown;
});
