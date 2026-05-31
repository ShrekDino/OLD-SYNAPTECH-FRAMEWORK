import 'package:flutter/material.dart';

abstract final class SamChatColors {
  SamChatColors._();

  static const background = Color(0xFF000000);
  static const surface = Color(0xFF111111);
  static const surfaceElevated = Color(0xFF1C1C1E);
  static const surfaceDim = Color(0xFF0A0A0A);

  static const onSurface = Color(0xFFE5E5E7);
  static const onSurfaceDim = Color(0xFF8E8E93);
  static const onSurfaceDisabled = Color(0xFF48484A);

  static const accentSilent = Color(0xFF007AFF);
  static const accentUrgent = Color(0xFFFF3B30);
  static const accentUrgentGlow = Color(0x40FF3B30);

  static const bubbleSent = Color(0xFF1E5CFF);
  static const bubbleReceived = Color(0xFF1C1C1E);
  static const bubbleBorderUrgent = Color(0xFFFF3B30);

  static const divider = Color(0xFF222224);
  static const overlay = Color(0x80000000);

  static const green = Color(0xFF30D158);
  static const yellow = Color(0xFFFFD60A);
  static const orange = Color(0xFFFF9F0A);

  static const inputBackground = Color(0xFF1A1A1C);
  static const inputBorder = Color(0xFF2C2C2E);
  static const inputBorderFocused = Color(0xFF3A3A3C);

  static const snackbarUrgent = Color(0xFF2E0A08);
  static const snackbarDefault = Color(0xFF1C1C1E);
}
