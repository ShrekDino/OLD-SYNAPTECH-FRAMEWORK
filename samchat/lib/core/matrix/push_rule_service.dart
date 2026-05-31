import 'dart:convert';
import 'package:http/http.dart' as http;

class PushRuleException implements Exception {
  final String message;
  final int? statusCode;
  PushRuleException(this.message, {this.statusCode});

  @override
  String toString() => 'PushRuleException: $message';
}

abstract final class PushRuleService {
  PushRuleService._();

  static const String _ruleId = '.org.custom.urgency';

  static Uri _buildUri(String homeserver) => Uri.parse(
        '$homeserver/_matrix/client/v3/pushrules/global/override/$_ruleId',
      );

  static Future<void> setupUrgentRule({
    required String homeserver,
    required String accessToken,
  }) async {
    final uri = _buildUri(homeserver);
    final body = jsonEncode({
      'actions': [
        'notify',
        {'set_tweak': 'sound', 'value': 'default'},
        {'set_tweak': 'highlight', 'value': true},
      ],
      'conditions': [
        {
          'kind': 'event_property_is',
          'key': 'content.org.custom.urgency',
          'value': 'urgent',
        },
      ],
    });

    final response = await http.put(
      uri,
      headers: _authHeaders(accessToken),
      body: body,
    );

    if (response.statusCode != 200) {
      throw PushRuleException(
        'Failed to create urgent push rule',
        statusCode: response.statusCode,
      );
    }
  }

  static Future<void> removeUrgentRule({
    required String homeserver,
    required String accessToken,
  }) async {
    final uri = _buildUri(homeserver);

    final response = await http.delete(
      uri,
      headers: _authHeaders(accessToken),
    );

    if (response.statusCode != 200 && response.statusCode != 404) {
      throw PushRuleException(
        'Failed to remove urgent push rule',
        statusCode: response.statusCode,
      );
    }
  }

  static Future<void> enableRule({
    required String homeserver,
    required String accessToken,
    required bool enabled,
  }) async {
    final uri = Uri.parse(
      '$homeserver/_matrix/client/v3/pushrules/global/override/$_ruleId/enabled',
    );
    final body = jsonEncode({'enabled': enabled});

    final response = await http.put(
      uri,
      headers: _authHeaders(accessToken),
      body: body,
    );

    if (response.statusCode != 200) {
      throw PushRuleException(
        'Failed to ${enabled ? 'enable' : 'disable'} push rule',
        statusCode: response.statusCode,
      );
    }
  }

  static Future<Map<String, dynamic>?> getRule({
    required String homeserver,
    required String accessToken,
  }) async {
    final uri = _buildUri(homeserver);

    final response = await http.get(
      uri,
      headers: _authHeaders(accessToken),
    );

    if (response.statusCode == 404) return null;
    if (response.statusCode != 200) {
      throw PushRuleException(
        'Failed to get push rule',
        statusCode: response.statusCode,
      );
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  static Map<String, String> _authHeaders(String accessToken) => {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      };
}
