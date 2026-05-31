import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    passed: bool
    reason: Optional[str] = None


DISALLOWED_IMPORTS = {
    'os', 'subprocess', 'sys', 'shutil', 'signal',
    'ctypes', 'socket', 'multiprocessing', 'threading',
    'fcntl', 'ptty', 'grp', 'pwd', 'resource',
    'crypt', 'termios', 'tty',
}

DISALLOWED_MODULE_PREFIXES = {
    'os.', 'subprocess.', 'ctypes.', 'socket.',
}

DISALLOWED_BUILTINS = {
    '__import__', 'exec', 'eval', 'compile',
    'open', 'input', 'breakpoint',
}

ALLOWED_IMPORTS = {
    'math', 'random', 'json', 'csv', 're', 'datetime',
    'collections', 'itertools', 'functools', 'typing',
    'pathlib', 'statistics', 'decimal', 'fractions',
    'string', 'textwrap', 'pprint', 'hashlib', 'base64',
    'uuid', 'bisect', 'heapq', 'array', 'enum',
    'copy', 'dataclasses', 'numbers', 'math',
    'numpy', 'pandas', 'scipy', 'matplotlib',
}


class CodeValidator:
    def validate(self, code_str, language='python'):
        if language == 'python':
            return self._validate_python(code_str)
        elif language in ('bash', 'shell'):
            return self._validate_bash(code_str)
        return ValidationResult(False, f'Unsupported language: {language}')

    def _validate_python(self, code_str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return ValidationResult(False, f'Syntax error: {e}')

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split('.')[0]
                    if name in DISALLOWED_IMPORTS:
                        return ValidationResult(False, f'Disallowed import: {alias.name}')
                    if name not in ALLOWED_IMPORTS and name not in DISALLOWED_IMPORTS:
                        return ValidationResult(False, f'Non-whitelisted import: {alias.name}. '
                                            f'Allowed: {sorted(ALLOWED_IMPORTS)[:20]}...')

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                base = module.split('.')[0]
                if base in DISALLOWED_IMPORTS:
                    return ValidationResult(False, f'Disallowed import from: {module}')
                if base not in ALLOWED_IMPORTS and base not in DISALLOWED_IMPORTS:
                    return ValidationResult(False, f'Non-whitelisted import from: {module}')

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DISALLOWED_BUILTINS:
                        return ValidationResult(False, f'Disallowed builtin: {node.func.id}')
                elif isinstance(node.func, ast.Attribute):
                    full_name = self._get_full_name(node.func)
                    if full_name and any(full_name.startswith(d) for d in DISALLOWED_MODULE_PREFIXES):
                        return ValidationResult(False, f'Disallowed module access: {full_name}')

            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id == '__builtins__':
                        return ValidationResult(False, 'Direct __builtins__ access disallowed')

        return ValidationResult(True)

    def _validate_bash(self, code_str):
        dangerous_commands = [
            'rm -rf', 'mkfs', 'dd if=', '> /dev/', 'sudo',
            'chmod 777', 'chown', 'kill -9', 'pkill',
            ':(){ :|:& };:',  # fork bomb
        ]
        for cmd in dangerous_commands:
            if cmd in code_str:
                return ValidationResult(False, f'Potentially dangerous command pattern: {cmd}')
        return ValidationResult(True)

    def _get_full_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_full_name(node.value)
            if base:
                return f'{base}.{node.attr}'
        return None
