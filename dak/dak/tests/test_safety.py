from dak.safety import SafetyConstitution, SafetyConstraints, SafetyMonitor, AuditLogger


def test_constitution_invariants():
    c = SafetyConstitution()
    invs = c.list_invariants()
    assert 'szilard_above_threshold' in invs
    assert 'constitution_integrity' in invs
    assert c.verify_integrity()


def test_constitution_invariant_toggle():
    c = SafetyConstitution()
    assert c.is_active('szilard_above_threshold')
    c.disable_invariant('szilard_above_threshold')
    assert not c.is_active('szilard_above_threshold')
    c.enable_invariant('szilard_above_threshold')
    assert c.is_active('szilard_above_threshold')


def test_constraints_param_bounds():
    sc = SafetyConstraints()
    ok, bounds = sc.check_param('LEARNING_RATE', 0.05)
    assert ok
    ok, bounds = sc.check_param('LEARNING_RATE', 100.0)
    assert not ok


def test_constraints_operational():
    sc = SafetyConstraints()
    violations = sc.check_operational(mu_norm=10.0, S_gen=1.0, F=100.0, tick_count=5)
    assert len(violations) == 0
    violations = sc.check_operational(mu_norm=2000.0, S_gen=1.0, F=100.0, tick_count=5)
    assert len(violations) == 1
    assert violations[0][0] == 'mu_norm'


def test_safety_monitor_clean():
    sm = SafetyMonitor()
    state = {
        'szilard_ratio': 5.0,
        'F': 100.0,
        'mu_norm': 5.0,
        'S_gen': 1.0,
        'tick_count': 10,
    }
    violations = sm.check(state)
    assert len(violations) == 0


def test_audit_logger(tmp_path):
    log_path = str(tmp_path / 'test_audit.jsonl')
    al = AuditLogger(path=log_path)
    al.log('test', 'pytest', {'msg': 'hello'})
    records = al.read_recent(10)
    assert len(records) == 1
    assert records[0]['type'] == 'test'
    assert records[0]['detail']['msg'] == 'hello'
