import subprocess


def test_sync_repo_state_check_passes():
    subprocess.run(["python3", "tools/sync_repo_state.py"], check=True)
    result = subprocess.run(["python3", "tools/sync_repo_state.py", "--check"], check=False)

    assert result.returncode == 0
