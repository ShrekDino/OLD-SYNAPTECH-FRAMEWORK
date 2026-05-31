import 'package:flutter/material.dart';

enum AccentColorOption {
  blue('Blue', Color(0xFF007AFF)),
  crimson('Crimson', Color(0xFFFF3B30)),
  purple('Purple', Color(0xFFAF52DE)),
  green('Green', Color(0xFF30D158)),
  orange('Orange', Color(0xFFFF9F0A)),
  yellow('Yellow', Color(0xFFFFD60A)),
  teal('Teal', Color(0xFF00C7BE)),
  pink('Pink', Color(0xFFFF6482));

  final String label;
  final Color color;
  const AccentColorOption(this.label, this.color);
}

enum ChatBubbleStyle {
  modern('Modern', BorderRadius.all(Radius.circular(16))),
  rounded('Rounded', BorderRadius.all(Radius.circular(22))),
  compact('Compact', BorderRadius.all(Radius.circular(10)));

  final String label;
  final BorderRadius radius;
  const ChatBubbleStyle(this.label, this.radius);
}

class AppSettings {
  final ThemeMode themeMode;
  final AccentColorOption accentColor;
  final bool urgentNotificationSound;
  final bool silentNotificationVibration;
  final bool showReadReceipts;
  final bool showTypingIndicators;
  final double fontSize;
  final bool enterToSend;
  final ChatBubbleStyle bubbleStyle;

  const AppSettings({
    this.themeMode = ThemeMode.dark,
    this.accentColor = AccentColorOption.blue,
    this.urgentNotificationSound = true,
    this.silentNotificationVibration = true,
    this.showReadReceipts = true,
    this.showTypingIndicators = true,
    this.fontSize = 16.0,
    this.enterToSend = false,
    this.bubbleStyle = ChatBubbleStyle.modern,
  });

  AppSettings copyWith({
    ThemeMode? themeMode,
    AccentColorOption? accentColor,
    bool? urgentNotificationSound,
    bool? silentNotificationVibration,
    bool? showReadReceipts,
    bool? showTypingIndicators,
    double? fontSize,
    bool? enterToSend,
    ChatBubbleStyle? bubbleStyle,
  }) {
    return AppSettings(
      themeMode: themeMode ?? this.themeMode,
      accentColor: accentColor ?? this.accentColor,
      urgentNotificationSound:
          urgentNotificationSound ?? this.urgentNotificationSound,
      silentNotificationVibration:
          silentNotificationVibration ?? this.silentNotificationVibration,
      showReadReceipts: showReadReceipts ?? this.showReadReceipts,
      showTypingIndicators: showTypingIndicators ?? this.showTypingIndicators,
      fontSize: fontSize ?? this.fontSize,
      enterToSend: enterToSend ?? this.enterToSend,
      bubbleStyle: bubbleStyle ?? this.bubbleStyle,
    );
  }

  Map<String, dynamic> toJson() => {
        'themeMode': themeMode.index,
        'accentColor': accentColor.index,
        'urgentNotificationSound': urgentNotificationSound,
        'silentNotificationVibration': silentNotificationVibration,
        'showReadReceipts': showReadReceipts,
        'showTypingIndicators': showTypingIndicators,
        'fontSize': fontSize,
        'enterToSend': enterToSend,
        'bubbleStyle': bubbleStyle.index,
      };

  factory AppSettings.fromJson(Map<String, dynamic> json) => AppSettings(
        themeMode: ThemeMode.values[json['themeMode'] as int? ?? 1],
        accentColor: AccentColorOption.values[
            json['accentColor'] as int? ?? 0],
        urgentNotificationSound:
            json['urgentNotificationSound'] as bool? ?? true,
        silentNotificationVibration:
            json['silentNotificationVibration'] as bool? ?? true,
        showReadReceipts: json['showReadReceipts'] as bool? ?? true,
        showTypingIndicators: json['showTypingIndicators'] as bool? ?? true,
        fontSize: (json['fontSize'] as num?)?.toDouble() ?? 16.0,
        enterToSend: json['enterToSend'] as bool? ?? false,
        bubbleStyle: ChatBubbleStyle
            .values[json['bubbleStyle'] as int? ?? 0],
      );
}
