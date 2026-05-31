import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ConnectivityQueue {
  static const _key = 'samchat_report_queue';

  Future<void> enqueue({
    required String title,
    required String body,
    required List<String> labels,
    required String repoOwner,
    required String repoName,
    required String pat,
  }) async {
    final entry = jsonEncode({
      'title': title,
      'body': body,
      'labels': labels,
      'repo_owner': repoOwner,
      'repo_name': repoName,
      'pat': pat,
    });

    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key) ?? '[]';
    try {
      final queue = jsonDecode(raw) as List<dynamic>;
      queue.add(entry);
      await prefs.setString(_key, jsonEncode(queue));
      debugPrint('[ConnectivityQueue] Enqueued: $title');
    } catch (e) {
      debugPrint('[ConnectivityQueue] Enqueue error: $e');
      await prefs.setString(_key, jsonEncode([entry]));
    }
  }

  Future<void> flush() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null || raw == '[]') return;

    try {
      final queue = jsonDecode(raw) as List<dynamic>;
      final remaining = <String>[];

      for (final entry in queue) {
        if (entry is! String) {
          remaining.add(entry.toString());
          continue;
        }

        try {
          final data = jsonDecode(entry) as Map<String, dynamic>;
          final sent = await _send(data);
          if (!sent) remaining.add(entry);
        } catch (e) {
          debugPrint('[ConnectivityQueue] Flush item error: $e');
          remaining.add(entry);
        }
      }

      await prefs.setString(_key, jsonEncode(remaining));
      if (remaining.isEmpty) {
        debugPrint('[ConnectivityQueue] Queue flushed successfully');
      }
    } catch (e) {
      debugPrint('[ConnectivityQueue] Flush error: $e');
    }
  }

  Future<bool> _send(Map<String, dynamic> data) async {
    final repoOwner = data['repo_owner'] as String?;
    final repoName = data['repo_name'] as String?;
    final pat = data['pat'] as String?;
    final title = data['title'] as String?;
    final body = data['body'] as String?;
    final labels = data['labels'] as List<dynamic>?;

    if (repoOwner == null || repoName == null || pat == null || title == null) {
      return false;
    }

    try {
      final url = 'https://api.github.com/repos/$repoOwner/$repoName/issues';
      final payload = jsonEncode({
        'title': title,
        'body': body ?? '',
        'labels': labels ?? [],
      });

      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $pat',
          'Accept': 'application/vnd.github+json',
          'Content-Type': 'application/json',
        },
        body: payload,
      );

      if (response.statusCode == 201) {
        final result = jsonDecode(response.body) as Map<String, dynamic>;
        debugPrint('[ConnectivityQueue] Created: ${result['html_url']}');
        return true;
      } else {
        debugPrint('[ConnectivityQueue] Failed (${response.statusCode}): ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('[ConnectivityQueue] Send error: $e');
      return false;
    }
  }

  Future<int> pendingCount() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null || raw == '[]') return 0;
    try {
      return (jsonDecode(raw) as List).length;
    } catch (_) {
      return 0;
    }
  }
}
