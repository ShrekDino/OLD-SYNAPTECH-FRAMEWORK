import 'dart:convert';

const _urgencyKey = 'org.custom.urgency';
const _urgentValue = 'urgent';

extension MatrixEventUrgency on Map<String, dynamic> {
  bool get isUrgent {
    final content = this['content'];
    if (content is Map<String, dynamic>) {
      return content[_urgencyKey] == _urgentValue;
    }
    if (content is String) {
      try {
        final parsed = jsonDecode(content) as Map<String, dynamic>;
        return parsed[_urgencyKey] == _urgentValue;
      } catch (_) {
        return false;
      }
    }
    return false;
  }

  bool get hasUrgencyFlag =>
      (this['content'] is Map<String, dynamic>) &&
      (this['content'] as Map<String, dynamic>).containsKey(_urgencyKey);
}

extension MessageContentUrgency on Map<String, dynamic> {
  Map<String, dynamic> withUrgency(bool urgent) {
    if (urgent) {
      this[_urgencyKey] = _urgentValue;
    } else {
      remove(_urgencyKey);
    }
    return this;
  }

  bool get isUrgentContent => this[_urgencyKey] == _urgentValue;
}
