import ast
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize('layer', ['domain', 'application'])
def test_core_dependencies_point_inwards(layer):
    app = Path(__file__).resolve().parents[2] / 'app'
    allowed = {'app.domain'}
    if layer == 'application':
        allowed.update({'app.application', 'email_validator'})
    violations = []
    for source in (app / layer).rglob('*.py'):
        for node in ast.walk(ast.parse(source.read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or '']
            for module in modules:
                if module.split('.')[0] in sys.stdlib_module_names:
                    continue
                if not any(
                    module == prefix or module.startswith(prefix + '.')
                    for prefix in allowed
                ):
                    violations.append(f'{source.name}: {module}')
    assert not violations, violations
