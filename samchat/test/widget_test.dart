import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:samchat/app.dart';
import 'package:samchat/core/services/shared_preferences_provider.dart';

void main() {
  testWidgets('SamChat app renders without error', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: const SamChatApp(),
      ),
    );

    expect(find.text('SamChat'), findsOneWidget);
  });
}
