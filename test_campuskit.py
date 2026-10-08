"""Run these plain checks with: python test_campuskit.py"""

import ast
import io
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

import campuskit as app

source = Path(app.__file__)
functions = []
for node in ast.walk(ast.parse(source.read_text())):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        functions.append(node)
assert len(functions) == 9
print("PASS: exactly 9 application functions, with no hidden nested functions or lambdas")

resources, fellows, records = app.create_initial_state()
assert [r['available'] for r in resources] == [10, 5, 3]
assert fellows == {'F001': 'Ada', 'F002': 'John', 'F003': 'Grace'} and records == []
other = app.create_initial_state()
resources[0]['available'] = 0
assert other[0][0]['available'] == 10
resources, fellows, records = app.create_initial_state()
print("PASS: exact starting quantities and independent sessions")

added = app.add_resource(resources, ' r004 ', ' Projector ', ' Electronics ', 2)
assert added == {'id': 'R004', 'name': 'Projector', 'category': 'Electronics', 'total': 2, 'available': 2}
before = deepcopy(resources)
for args in [('r001', 'Other', 'Other', 1), ('', 'Other', 'Other', 1), ('R005', '', 'Other', 1),
             ('R005', 'Other', ' ', 1), ('R005', 'Other', 'Other', 0), ('R005', 'Other', 'Other', True)]:
    try:
        app.add_resource(resources, *args)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid resource accepted')
    assert resources == before
print("PASS: additions, normalization, duplicates, blank fields and invalid totals")

resources, fellows, records = app.create_initial_state()
assert app.borrow_resource(resources, fellows, records, ' f001 ', ' r001 ', 2) == 8
assert app.borrow_resource(resources, fellows, records, 'F002', 'R002', 3) == 2
assert app.return_resource(resources, fellows, records, 'F001', 'R001', 1) == 9
before = deepcopy((resources, fellows, records))
cases = [('F999', 'R001', 1), ('F001', 'R999', 1), ('F001', 'R001', 0),
         ('F001', 'R001', -1), ('F001', 'R001', 1.5), ('F001', 'R001', 'two'),
         ('F001', 'R001', True), (None, 'R001', 1), ('F001', None, 1)]
for operation in (app.borrow_resource, app.return_resource):
    for args in cases:
        try:
            operation(resources, fellows, records, *args)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid transaction accepted')
        assert (resources, fellows, records) == before
for operation, args in [(app.borrow_resource, ('F003', 'R003', 4)),
                        (app.return_resource, ('F002', 'R002', 4)),
                        (app.return_resource, ('F003', 'R001', 1))]:
    try:
        operation(resources, fellows, records, *args)
    except ValueError:
        pass
    else:
        raise AssertionError('Excessive transaction accepted')
    assert (resources, fellows, records) == before
print("PASS: required transactions and rejected requests preserve all state")

assert app.search_resources(resources, ' LAPtop ') == [resources[0]]
assert app.search_resources(resources, 'lap') == [resources[0]]
assert app.search_resources(resources, 'ACCESSORIES', True) == resources[1:]
assert app.search_resources(resources, 'Access', True) == []
assert app.search_resources([], 'Laptop') == []
for query in ('', ' ', None):
    try:
        app.search_resources(resources, query)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid search accepted')
with redirect_stdout(io.StringIO()):
    report = app.generate_report(resources)
assert (report['total'], report['available'], report['borrowed']) == (18, 14, 4)
assert report['low_stock'] == [resources[1]] and report['most_borrowed'] == [resources[1]]
assert (resources, fellows, records) == before
print("PASS: search, category filter, required report and read-only state preservation")

resources, fellows, records = app.create_initial_state()
for rid in ('R001', 'R002', 'R003'):
    app.borrow_resource(resources, fellows, records, 'F001', rid, 3)
with redirect_stdout(io.StringIO()):
    report = app.generate_report(resources)
assert report['most_borrowed'] == resources
assert [r['available'] for r in report['low_stock']] == [2, 0]
app.return_resource(resources, fellows, records, 'F001', 'R001', 3)
with redirect_stdout(io.StringIO()):
    assert app.generate_report(resources)['most_borrowed'] == resources[1:]
for rid in ('R002', 'R003'):
    app.return_resource(resources, fellows, records, 'F001', rid, 3)
with redirect_stdout(io.StringIO()):
    assert app.generate_report(resources)['most_borrowed'] == []
    empty = app.generate_report([])
assert (empty['total'], empty['available'], empty['borrowed']) == (0, 0, 0)
assert empty['most_borrowed'] == [] and empty['low_stock'] == []
print("PASS: all tied leaders, zero stock, threshold of 3, current rather than historical loans, empty reports")

resources, fellows, records = app.create_initial_state()
app.borrow_resource(resources, fellows, records, 'F001', 'R001', 2)
app.borrow_resource(resources, fellows, records, 'F002', 'R001', 1)
app.borrow_resource(resources, fellows, records, 'F001', 'R001', 3)
app.return_resource(resources, fellows, records, 'F001', 'R001', 4)
assert [r['quantity_returned'] for r in records] == [2, 0, 2]
assert resources[0]['available'] == 8
before = deepcopy((resources, fellows, records))
try:
    app.return_resource(resources, fellows, records, 'F001', 'R001', 2)
except ValueError:
    pass
else:
    raise AssertionError('Excessive return accepted')
assert (resources, fellows, records) == before
app.return_resource(resources, fellows, records, 'F001', 'R001', 1)
assert records[2]['quantity_returned'] == 3 and len(records) == 3
try:
    app.return_resource(resources, fellows, records, 'F001', 'R001', 1)
except ValueError:
    pass
else:
    raise AssertionError('Double return accepted')
print("PASS: partial/full returns across oldest loans, other fellows unaffected, history retained")

resources, fellows, records = app.create_initial_state()
app.borrow_resource(resources, fellows, records, 'F001', 'R003', 3)
before = deepcopy((resources, fellows, records))
try:
    app.borrow_resource(resources, fellows, records, 'F002', 'R003', 1)
except ValueError:
    pass
else:
    raise AssertionError('Zero-stock borrowing accepted')
assert (resources, fellows, records) == before
print("PASS: borrowing exact stock and rejecting further borrowing")

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    program = root / 'campuskit.py'
    program.write_bytes(source.read_bytes())
    (root / 'old-save.json').write_text('Leave this old file alone')
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    inputs = 'wrong\n2\nR004\nProjector\nElectronics\n2\n3\nF001\nR001\ntwo\n3\nF001\nR001\n2\n4\nF001\nR001\n1\n5\nLAPtop\n6\nAccessories\n7\n8\n0\n'
    result = subprocess.run([sys.executable, str(program)], input=inputs, text=True, capture_output=True, timeout=5)
    assert result.returncode == 0 and result.stderr == ''
    for text in ('Invalid option', 'Invalid input', 'Resource added.', 'Available now: 8',
                 'Available now: 9', 'Total units: 20', 'F001: Ada'):
        assert text in result.stdout, text
    result = subprocess.run([sys.executable, str(program)], input='7\n0\n', text=True, capture_output=True, timeout=5)
    assert 'Total units: 18' in result.stdout and 'Units currently borrowed: 0' in result.stdout
    result = subprocess.run([sys.executable, str(program)], input='3\nF001\n', text=True, capture_output=True, timeout=5)
    assert result.returncode == 0 and 'Input ended.' in result.stdout
    after = {p.name: p.read_bytes() for p in root.iterdir()}
    assert after == before
print("PASS: interactive flow, invalid text, EOF, fresh restart and no file changes")

result = subprocess.run([sys.executable, str(source), '--demo'], text=True, capture_output=True, timeout=5)
assert result.returncode == 0 and result.stderr == ''
assert 'All seven steps and the additional invalid-input test: PASS' in result.stdout
print("PASS: standalone demonstration")
print("All checks passed.")
