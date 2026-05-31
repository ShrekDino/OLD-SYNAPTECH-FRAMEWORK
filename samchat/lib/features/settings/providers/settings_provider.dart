import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_settings.dart';
import '../../../core/services/shared_preferences_provider.dart';

const _settingsKey = 'samchat_settings';

class SettingsNotifier extends StateNotifier<AppSettings> {
  final SharedPreferences _prefs;

  SettingsNotifier(this._prefs) : super(const AppSettings()) {
    _load();
  }

  void _load() {
    try {
      final raw = _prefs.getString(_settingsKey);
      if (raw != null) {
        final json = jsonDecode(raw) as Map<String, dynamic>;
        state = AppSettings.fromJson(json);
        debugPrint('[Settings] Loaded: ${state.accentColor.label} / ${state.themeMode.name}');
      }
    } catch (e) {
      debugPrint('[Settings] Failed to load: $e');
    }
  }

  Future<void> _persist() async {
    try {
      await _prefs.setString(_settingsKey, jsonEncode(state.toJson()));
    } catch (e) {
      debugPrint('[Settings] Failed to persist: $e');
    }
  }

  void setThemeMode(ThemeMode mode) {
    state = state.copyWith(themeMode: mode);
    _persist();
  }

  void setAccentColor(AccentColorOption color) {
    state = state.copyWith(accentColor: color);
    _persist();
  }

  void setUrgentNotificationSound(bool value) {
    state = state.copyWith(urgentNotificationSound: value);
    _persist();
  }

  void setSilentNotificationVibration(bool value) {
    state = state.copyWith(silentNotificationVibration: value);
    _persist();
  }

  void setShowReadReceipts(bool value) {
    state = state.copyWith(showReadReceipts: value);
    _persist();
  }

  void setShowTypingIndicators(bool value) {
    state = state.copyWith(showTypingIndicators: value);
    _persist();
  }

  void setFontSize(double size) {
    state = state.copyWith(fontSize: size);
    _persist();
  }

  void setEnterToSend(bool value) {
    state = state.copyWith(enterToSend: value);
    _persist();
  }

  void setBubbleStyle(ChatBubbleStyle style) {
    state = state.copyWith(bubbleStyle: style);
    _persist();
  }
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, AppSettings>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SettingsNotifier(prefs);
});
