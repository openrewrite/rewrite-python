import textwrap

import mypy.api


def test_run_mypy_on_valid_code():
    code = textwrap.dedent("""
    def add(a: int, b: int) -> int:
        return a + b

    result = add(1, 2)
    print(result)
    """)
    stdout, stderr, exit_code = run_mypy_on_code(code)

    assert "Success: no issues found" in stdout
    assert stderr == ""
    assert exit_code == 0

def run_mypy_on_code(code: str):
    result = mypy.api.run(["-c", code])
    stdout, stderr, exit_code = result
    return stdout, stderr, exit_code