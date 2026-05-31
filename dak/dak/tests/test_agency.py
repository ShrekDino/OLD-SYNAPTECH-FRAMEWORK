from dak.agency.sandbox import Sandbox
from dak.agency.workspace import Workspace
from dak.agency.code_validator import CodeValidator
from dak.agency.safety_sentinel import SafetySentinel
from dak.safety.monitor import SafetyMonitor


def test_sandbox_run_python():
    s = Sandbox(work_dir='/tmp/erebus_test_sbox')
    result = s.run_code('print("hello from erebus")')
    assert result.exit_code == 0
    assert 'hello from erebus' in result.stdout
    s.cleanup()


def test_sandbox_timeout():
    s = Sandbox(timeout=0.5, work_dir='/tmp/erebus_test_sbox')
    result = s.run_code('import time; time.sleep(10)')
    assert result.timed_out
    s.cleanup()


def test_sandbox_run_bash():
    s = Sandbox(work_dir='/tmp/erebus_test_sbox')
    result = s.run_code('echo "erebus test"', language='bash')
    assert result.exit_code == 0
    assert 'erebus test' in result.stdout
    s.cleanup()


def test_workspace_read_write():
    w = Workspace(root='/tmp/erebus_test_ws')
    w.write_file('test.txt', 'hello erebus')
    content = w.read_file('test.txt')
    assert content == 'hello erebus'
    w.clear()


def test_workspace_escape_detection():
    w = Workspace(root='/tmp/erebus_test_ws')
    try:
        w.read_file('/etc/passwd')
        assert False, 'Should have raised PermissionError'
    except PermissionError:
        pass
    w.clear()


def test_workspace_snapshot_rollback():
    w = Workspace(root='/tmp/erebus_test_ws')
    w.write_file('state.txt', 'before')
    w.snapshot()
    w.write_file('state.txt', 'after')
    w.rollback()
    content = w.read_file('state.txt')
    assert content == 'before'
    w.clear()


def test_code_validator_good_code():
    v = CodeValidator()
    result = v.validate('x = 42\nprint(x * 2)')
    assert result.passed


def test_code_validator_bad_import():
    v = CodeValidator()
    result = v.validate('import os\nos.system("rm -rf /")')
    assert not result.passed
    assert 'Disallowed import' in result.reason


def test_code_validator_bad_builtin():
    v = CodeValidator()
    result = v.validate('exec("print(1)")')
    assert not result.passed
    assert 'Disallowed builtin' in result.reason


def test_code_validator_bad_bash():
    v = CodeValidator()
    result = v.validate('sudo rm -rf /', language='bash')
    assert not result.passed


def test_safety_sentinel_init():
    sbox = Sandbox(work_dir='/tmp/erebus_test_sent')
    ws = Workspace(root='/tmp/erebus_test_sent_ws')
    mon = SafetyMonitor()
    sentinel = SafetySentinel(sbox, ws, mon)
    assert sentinel is not None
    sbox.cleanup()
    ws.clear()
