import subprocess


def test_smoke_tool():
    result = subprocess.run(["python3", "tools/smoke_test.py"], check=False)

    assert result.returncode == 0
