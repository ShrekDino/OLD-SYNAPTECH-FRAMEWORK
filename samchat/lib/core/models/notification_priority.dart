enum NotificationPriority {
  silent,
  urgent;

  bool get isUrgent => this == NotificationPriority.urgent;
  bool get isSilent => this == NotificationPriority.silent;

  NotificationPriority toggle() =>
      this == NotificationPriority.silent ? NotificationPriority.urgent : NotificationPriority.silent;

  String toJson() => name;

  static NotificationPriority fromJson(String json) =>
      NotificationPriority.values.firstWhere((e) => e.name == json, orElse: () => NotificationPriority.silent);
}
