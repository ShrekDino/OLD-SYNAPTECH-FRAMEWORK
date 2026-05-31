import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:matrix/matrix.dart';
import '../../../core/design/app_colors.dart';
import '../../../features/auth/state/auth_notifier.dart';

class _ServerOption {
  final String name;
  final String domain;
  final String description;
  final String iconLetter;
  final Color iconColor;

  const _ServerOption({
    required this.name,
    required this.domain,
    required this.description,
    required this.iconLetter,
    required this.iconColor,
  });
}

const _servers = [
  _ServerOption(
    name: 'Matrix HQ',
    domain: 'matrix.org',
    description: 'Official Matrix homeserver',
    iconLetter: 'M',
    iconColor: Color(0xFF00C853),
  ),
  _ServerOption(
    name: 'Mozilla',
    domain: 'mozilla.org',
    description: 'Mozilla community server',
    iconLetter: 'MZ',
    iconColor: Color(0xFFFF9400),
  ),
  _ServerOption(
    name: 'tchncs',
    domain: 'tchncs.de',
    description: 'German privacy-focused provider',
    iconLetter: 'T',
    iconColor: Color(0xFF2196F3),
  ),
  _ServerOption(
    name: '0x0a Space',
    domain: '0x0a.space',
    description: 'Community-run Matrix server',
    iconLetter: '0A',
    iconColor: Color(0xFF9C27B0),
  ),
  _ServerOption(
    name: 'envs.net',
    domain: 'envs.net',
    description: 'Open source community server',
    iconLetter: 'EN',
    iconColor: Color(0xFFE91E63),
  ),
  _ServerOption(
    name: 'Aria',
    domain: 'aria-net.org',
    description: 'Italian Matrix homeserver',
    iconLetter: 'AR',
    iconColor: Color(0xFF00BCD4),
  ),
];

enum _LoginStep { picker, probing, passwordLogin, ssoLogin }

class HomeserverPickerView extends ConsumerStatefulWidget {
  const HomeserverPickerView({super.key});

  @override
  ConsumerState<HomeserverPickerView> createState() =>
      _HomeserverPickerViewState();
}

class _HomeserverPickerViewState extends ConsumerState<HomeserverPickerView>
    with SingleTickerProviderStateMixin {
  _LoginStep _step = _LoginStep.picker;
  _ServerOption? _selectedServer;
  Client? _probe;
  bool _hasSso = false;

  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _customUrlController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _obscurePassword = true;
  bool _isCustomExpanded = false;

  late AnimationController _fadeCtrl;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _fadeCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);
    _fadeCtrl.forward();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _customUrlController.dispose();
    _fadeCtrl.dispose();
    super.dispose();
  }

  String _resolveHomeserverUrl(_ServerOption? srv) {
    if (srv != null) return 'https://${srv.domain}';
    final custom = _customUrlController.text.trim();
    if (custom.contains('://')) return custom;
    return 'https://$custom';
  }

  void _onSelectServer(_ServerOption srv) {
    setState(() => _selectedServer = srv);
    if (_isCustomExpanded) {
      setState(() => _isCustomExpanded = false);
    }
    _animateIn();
  }

  void _animateIn() {
    _fadeCtrl.reset();
    _fadeCtrl.forward();
  }

  void _onTapContinue() async {
    if (_selectedServer == null && _customUrlController.text.trim().isEmpty) {
      return;
    }
    final url = _resolveHomeserverUrl(_selectedServer);
    setState(() => _step = _LoginStep.probing);

    try {
      final probe = Client('SamChat');
      await probe.checkHomeserver(Uri.parse(url));

      final loginFlows = await probe.getLoginFlows();
      final hasSso = loginFlows?.any((f) =>
              f.type == AuthenticationTypes.sso ||
              f.type == AuthenticationTypes.oauth2) ??
          false;
      final hasPassword = loginFlows?.any(
              (f) => f.type == AuthenticationTypes.password) ??
          true;

      _probe = probe;
      _hasSso = hasSso;

      if (hasPassword) {
        setState(() => _step = _LoginStep.passwordLogin);
      } else if (hasSso) {
        setState(() => _step = _LoginStep.ssoLogin);
      } else {
        setState(() {
          _step = _LoginStep.picker;
          _selectedServer = null;
        });
        _showError('This server does not support password or SSO login.');
      }
    } on Exception catch (e) {
      debugPrint('[HomeserverPickerView] Server probe failed: $e');
      setState(() {
        _step = _LoginStep.picker;
        _selectedServer = null;
      });
      _showError('Could not connect to $url.\n$e');
    }

    _animateIn();
  }

  void _goBack() {
    setState(() {
      _step = _LoginStep.picker;
      _probe = null;
    });
    _animateIn();
  }

  void _showError(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: SamChatColors.accentSilent,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _handlePasswordLogin() {
    if (!_formKey.currentState!.validate()) return;
    if (_probe == null) return;

    ref.read(authNotifierProvider.notifier).loginWithPassword(
          probe: _probe!,
          username: _usernameController.text.trim(),
          password: _passwordController.text,
        );
  }

  void _handleSsoLogin() {
    if (_probe == null) return;
    ref.read(authNotifierProvider.notifier).loginWithSso(_probe!);
  }

  void _showHomeserverInfo() {
    showModalBottomSheet(
      context: context,
      backgroundColor: SamChatColors.surfaceElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: SamChatColors.accentSilent.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.info_outline_rounded,
                      color: SamChatColors.accentSilent,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'What is a homeserver?',
                    style: TextStyle(
                      color: SamChatColors.onSurface,
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              const Text(
                'A homeserver is like your email provider — it hosts your '
                'account and messages. Anyone can run their own server, '
                'just like anyone can run their own email server.',
                style: TextStyle(
                  color: SamChatColors.onSurfaceDim,
                  fontSize: 15,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Pick any public server from the list, or enter a custom '
                'one if you know the address. All Matrix servers can talk '
                'to each other, so you can message anyone on any server.',
                style: TextStyle(
                  color: SamChatColors.onSurfaceDim,
                  fontSize: 15,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authNotifierProvider);

    ref.listen<AuthState>(authNotifierProvider, (prev, next) {
      if (next.status == AuthStatus.error && next.error != null) {
        _showError(next.error!);
      } else if (next.status == AuthStatus.disconnected && next.error != null) {
        _showError(next.error!);
      }
    });

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: _buildBody(authState),
        ),
      ),
    );
  }

  Widget _buildBody(AuthState authState) {
    switch (_step) {
      case _LoginStep.picker:
        return _buildPicker(authState);
      case _LoginStep.probing:
        return _buildProbing();
      case _LoginStep.passwordLogin:
        return _buildPasswordForm(authState);
      case _LoginStep.ssoLogin:
        return _buildSsoForm(authState);
    }
  }

  Widget _buildPicker(AuthState authState) {
    final isBusy = authState.status == AuthStatus.loggingIn ||
        authState.status == AuthStatus.restoring;

    return Column(
      children: [
        const SizedBox(height: 16),
        _buildHeader(),
        const SizedBox(height: 28),
        Expanded(
          child: _buildServerList(isBusy),
        ),
        _buildContinueSection(isBusy),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        children: [
          GestureDetector(
            onTap: _showHomeserverInfo,
            child: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: SamChatColors.accentSilent.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Icon(
                  Icons.info_outline_rounded,
                  color: SamChatColors.accentSilent,
                  size: 22,
                ),
              ),
            ),
          ),
          const Spacer(),
          Column(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: SamChatColors.accentSilent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Center(
                  child: Text(
                    'SC',
                    style: TextStyle(
                      color: SamChatColors.accentSilent,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'SamChat',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Pick your homeserver',
                style: TextStyle(
                  color: Colors.grey[500],
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const Spacer(),
          const SizedBox(width: 44),
        ],
      ),
    );
  }

  Widget _buildServerList(bool isBusy) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      children: [
        ..._servers.map((srv) => _buildServerCard(srv, isBusy)),
        const SizedBox(height: 8),
        _buildCustomServerCard(),
      ],
    );
  }

  Widget _buildServerCard(_ServerOption srv, bool isBusy) {
    final isSelected = _selectedServer == srv;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: GestureDetector(
        onTap: isBusy ? null : () => _onSelectServer(srv),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            color: isSelected
                ? SamChatColors.accentSilent.withValues(alpha: 0.08)
                : SamChatColors.surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: isSelected ? SamChatColors.accentSilent : SamChatColors.divider,
              width: isSelected ? 1.5 : 1,
            ),
          ),
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: srv.iconColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    srv.iconLetter,
                    style: TextStyle(
                      color: srv.iconColor,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      srv.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      srv.domain,
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 1),
                    Text(
                      srv.description,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (isSelected)
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: SamChatColors.accentSilent,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.check_rounded,
                    color: Colors.white,
                    size: 16,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCustomServerCard() {
    return GestureDetector(
      onTap: () => setState(() => _isCustomExpanded = !_isCustomExpanded),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOutCubic,
        decoration: BoxDecoration(
          color: _isCustomExpanded
              ? SamChatColors.accentSilent.withValues(alpha: 0.08)
              : SamChatColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: _isCustomExpanded
                ? SamChatColors.accentSilent
                : SamChatColors.divider,
            width: _isCustomExpanded ? 1.5 : 1,
          ),
        ),
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: SamChatColors.accentSilent.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.link_rounded,
                      color: SamChatColors.accentSilent,
                      size: 22,
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Custom server',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Enter a custom homeserver URL',
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                AnimatedRotation(
                  turns: _isCustomExpanded ? 0.5 : 0,
                  duration: const Duration(milliseconds: 200),
                  child: Icon(
                    Icons.expand_more_rounded,
                    color: Colors.grey[500],
                    size: 24,
                  ),
                ),
              ],
            ),
            AnimatedCrossFade(
              firstChild: const SizedBox.shrink(),
              secondChild: Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Container(
                  decoration: BoxDecoration(
                    color: SamChatColors.inputBackground,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: SamChatColors.inputBorder),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Row(
                    children: [
                      Icon(Icons.link, color: Colors.grey[600], size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextField(
                          controller: _customUrlController,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                          decoration: InputDecoration(
                            hintText: 'https://custom.server.com',
                            hintStyle: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 14,
                            ),
                            border: InputBorder.none,
                            isDense: true,
                            contentPadding:
                                const EdgeInsets.symmetric(vertical: 14),
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      if (_customUrlController.text.trim().isNotEmpty)
                        GestureDetector(
                          onTap: () {
                            _customUrlController.clear();
                            setState(() {});
                          },
                          child: Icon(
                            Icons.close_rounded,
                            color: Colors.grey[600],
                            size: 18,
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              crossFadeState: _isCustomExpanded
                  ? CrossFadeState.showSecond
                  : CrossFadeState.showFirst,
              duration: const Duration(milliseconds: 200),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContinueSection(bool isBusy) {
    final hasSelection = _selectedServer != null ||
        (_isCustomExpanded && _customUrlController.text.trim().isNotEmpty);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SizedBox(
        width: double.infinity,
        height: 52,
        child: AnimatedOpacity(
          duration: const Duration(milliseconds: 200),
          opacity: hasSelection ? 1.0 : 0.4,
          child: ElevatedButton(
            onPressed: hasSelection && !isBusy ? _onTapContinue : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: SamChatColors.accentSilent,
              foregroundColor: Colors.white,
              disabledBackgroundColor: Colors.grey[800],
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: isBusy
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: Colors.white,
                    ),
                  )
                : const Text(
                    'Continue',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildProbing() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              color: _selectedServer?.iconColor ?? SamChatColors.accentSilent,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Connecting to ${_selectedServer?.name ?? 'server'}...',
            style: const TextStyle(color: Colors.white, fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            _resolveHomeserverUrl(_selectedServer),
            style: TextStyle(color: Colors.grey[500], fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildPasswordForm(AuthState authState) {
    final isBusy = authState.status == AuthStatus.loggingIn;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          const SizedBox(height: 32),
          _buildServerIdentity(),
          const SizedBox(height: 36),
          Form(
            key: _formKey,
            child: Column(
              children: [
                TextFormField(
                  controller: _usernameController,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                  decoration: _inputDecoration('Matrix ID', '@user:server'),
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) {
                      return 'Enter your Matrix ID';
                    }
                    if (!v.contains(':')) {
                      return 'Full MXID required (e.g. @user:server)';
                    }
                    return null;
                  },
                  enabled: !isBusy,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                  decoration: _inputDecoration('Password', null).copyWith(
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_off
                            : Icons.visibility,
                        color: Colors.grey[500],
                      ),
                      onPressed: () =>
                          setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Enter your password';
                    return null;
                  },
                  enabled: !isBusy,
                  onFieldSubmitted:
                      isBusy ? null : (_) => _handlePasswordLogin(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: isBusy ? null : _handlePasswordLogin,
              style: ElevatedButton.styleFrom(
                backgroundColor: SamChatColors.accentSilent,
                foregroundColor: Colors.white,
                disabledBackgroundColor: Colors.grey[800],
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: isBusy
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: Colors.white,
                      ),
                    )
                  : const Text(
                      'Sign In',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
            ),
          ),
          if (_hasSso) ...[
            const SizedBox(height: 12),
            _ssoDivider(),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: OutlinedButton.icon(
                onPressed: isBusy ? null : _handleSsoLogin,
                icon: const Icon(
                  Icons.fingerprint,
                  color: SamChatColors.accentSilent,
                  size: 22,
                ),
                label: const Text(
                  'Sign In with SSO',
                  style: TextStyle(
                    color: SamChatColors.accentSilent,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: SamChatColors.accentSilent),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
            ),
          ],
          const SizedBox(height: 24),
          _buildBackButton(isBusy),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildServerIdentity() {
    return Column(
      children: [
        Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            color: _selectedServer?.iconColor.withValues(alpha: 0.2) ??
                SamChatColors.accentSilent.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Center(
            child: Text(
              _selectedServer?.iconLetter ?? '?',
              style: TextStyle(
                color: _selectedServer?.iconColor ?? SamChatColors.accentSilent,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(height: 14),
        Text(
          _selectedServer?.name ?? 'Custom Server',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          _resolveHomeserverUrl(_selectedServer),
          style: TextStyle(color: Colors.grey[500], fontSize: 13),
        ),
      ],
    );
  }

  Widget _ssoDivider() {
    return Row(
      children: [
        Expanded(child: Container(height: 1, color: Colors.grey[800])),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text(
            'or',
            style: TextStyle(color: Colors.grey[500], fontSize: 13),
          ),
        ),
        Expanded(child: Container(height: 1, color: Colors.grey[800])),
      ],
    );
  }

  Widget _buildBackButton(bool isBusy) {
    return TextButton.icon(
      onPressed: isBusy ? null : _goBack,
      icon: Icon(Icons.arrow_back, color: Colors.grey[400], size: 18),
      label: Text(
        'Choose a different server',
        style: TextStyle(color: Colors.grey[400]),
      ),
    );
  }

  Widget _buildSsoForm(AuthState authState) {
    final isBusy = authState.status == AuthStatus.loggingIn;

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildServerIdentity(),
            const SizedBox(height: 48),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: isBusy ? null : _handleSsoLogin,
                icon: isBusy
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.fingerprint, size: 22),
                label: Text(
                  isBusy ? 'Signing in...' : 'Sign In with SSO',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SamChatColors.accentSilent,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'You will be redirected to your browser to complete authentication.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[500], fontSize: 13),
            ),
            const SizedBox(height: 32),
            _buildBackButton(isBusy),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String label, String? hint) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      labelStyle: TextStyle(color: Colors.grey[400], fontSize: 14),
      hintStyle: TextStyle(color: Colors.grey[600], fontSize: 14),
      filled: true,
      fillColor: Colors.grey[900],
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey[800]!),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey[800]!),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: SamChatColors.accentSilent, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
            color: SamChatColors.accentSilent.withValues(alpha: 0.7)),
      ),
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
    );
  }
}
