class PackUsage {
  final String value;
  const PackUsage._(this.value);

  static const emoticon = PackUsage._('emoticon');
  static const sticker = PackUsage._('sticker');

  static PackUsage fromString(String value) {
    switch (value) {
      case 'emoticon':
        return PackUsage.emoticon;
      case 'sticker':
        return PackUsage.sticker;
      default:
        return PackUsage._(value);
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) || other is PackUsage && value == other.value;

  @override
  int get hashCode => value.hashCode;

  @override
  String toString() => value;
}

class PackInfo {
  final String? displayName;
  final String? avatarUrl;
  final List<PackUsage> usage;
  final String? attribution;

  const PackInfo({
    this.displayName,
    this.avatarUrl,
    this.usage = const [],
    this.attribution,
  });

  bool get isStickerPack =>
      usage.isEmpty || usage.contains(PackUsage.sticker);

  factory PackInfo.fromJson(Map<String, dynamic> json) {
    final rawUsage = json['usage'];
    final usageList = <PackUsage>[];
    if (rawUsage is List) {
      for (final u in rawUsage) {
        if (u is String) usageList.add(PackUsage.fromString(u));
      }
    }
    return PackInfo(
      displayName: json['display_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      usage: usageList,
      attribution: json['attribution'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        if (displayName != null) 'display_name': displayName,
        if (avatarUrl != null) 'avatar_url': avatarUrl,
        if (usage.isNotEmpty) 'usage': usage.map((u) => u.value).toList(),
        if (attribution != null) 'attribution': attribution,
      };
}

class PackImage {
  final String url;
  final String? body;
  final Map<String, dynamic>? info;

  const PackImage({
    required this.url,
    this.body,
    this.info,
  });

  factory PackImage.fromJson(Map<String, dynamic> json) => PackImage(
        url: json['url'] as String,
        body: json['body'] as String?,
        info: json['info'] as Map<String, dynamic>?,
      );

  Map<String, dynamic> toJson() => {
        'url': url,
        if (body != null) 'body': body,
        if (info != null) 'info': info,
      };
}

class MatrixImagePack {
  final String packId;
  final String roomId;
  final Map<String, PackImage> images;
  final PackInfo? pack;

  const MatrixImagePack({
    required this.packId,
    required this.roomId,
    this.images = const {},
    this.pack,
  });

  bool get isStickerPack => pack?.isStickerPack ?? true;

  String get displayName =>
      pack?.displayName ?? packId;

  String? get avatarUrl => pack?.avatarUrl;

  factory MatrixImagePack.fromStateEvent({
    required String packId,
    required String roomId,
    required Map<String, dynamic> content,
  }) {
    final rawImages = content['images'] as Map<String, dynamic>? ?? {};
    final images = <String, PackImage>{};
    rawImages.forEach((key, value) {
      if (value is Map<String, dynamic>) {
        images[key] = PackImage.fromJson(value);
      }
    });

    final rawPack = content['pack'];
    final pack = rawPack is Map<String, dynamic>
        ? PackInfo.fromJson(rawPack)
        : null;

    return MatrixImagePack(
      packId: packId,
      roomId: roomId,
      images: images,
      pack: pack,
    );
  }
}
