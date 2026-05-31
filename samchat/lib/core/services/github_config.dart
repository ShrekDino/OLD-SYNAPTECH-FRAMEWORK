class GitHubConfig {
  final String repoOwner;
  final String repoName;
  final String? pat;

  const GitHubConfig({
    this.repoOwner = 'ShrekDino',
    this.repoName = 'samchat-reports',
    this.pat,
  });

  bool get isConfigured => pat != null && pat!.isNotEmpty;

  static GitHubConfig fromEnvironment() {
    return GitHubConfig(
      pat: const String.fromEnvironment('GITHUB_PAT', defaultValue: ''),
    );
  }
}
