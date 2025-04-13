import pytest
from dev_tools.git_tools.git_tool import run_git_command, check_branch_exists, generate_commit_overview

def fake_run_success(args, cwd=None, **kwargs):
    if "--graph" in args:
        class Dummy:
            pass
        dummy = Dummy()
        dummy.returncode = 0
        dummy.stdout = "* abc123 | Commit 1\n* def456 | Commit 2"
        dummy.stderr = ""
        return dummy
    else:
        class Dummy:
            pass
        dummy = Dummy()
        dummy.returncode = 0
        dummy.stdout = "abc123|John Doe|01-04-2025\ndef456|Jane Doe|02-04-2025"
        dummy.stderr = ""
        return dummy

def fake_run_failure(args, cwd=None, **kwargs):
    class Dummy:
        pass
    dummy = Dummy()
    dummy.returncode = 1
    dummy.stdout = ""
    dummy.stderr = "error message"
    return dummy

def test_run_git_command_success(monkeypatch):
    # Patch subprocess.run in our module to return a successful dummy output.
    monkeypatch.setattr("dev_tools.git_tools.git_tool.subprocess.run", fake_run_success)
    output = run_git_command(["log", "--pretty=format:%H|%an|%ad"])
    # Since run_git_command returns result.stdout, we can safely call strip()
    assert "abc123|John Doe|01-04-2025" in output

def test_run_git_command_failure(monkeypatch):
    monkeypatch.setattr("dev_tools.git_tools.git_tool.subprocess.run", fake_run_failure)
    with pytest.raises(SystemExit):
        run_git_command(["log"])

def test_check_branch_exists_success(monkeypatch):
    def fake_run_branch(args, cwd=None, **kwargs):
        class Dummy:
            pass
        dummy = Dummy()
        dummy.returncode = 0
        dummy.stdout = "branch exists"
        dummy.stderr = ""
        return dummy
    monkeypatch.setattr("dev_tools.git_tools.git_tool.subprocess.run", fake_run_branch)
    # Should complete without error.
    check_branch_exists("develop")

def test_check_branch_exists_failure(monkeypatch):
    def fake_run_branch_fail(args, cwd=None, **kwargs):
        class Dummy:
            pass
        dummy = Dummy()
        dummy.returncode = 1
        dummy.stdout = ""
        dummy.stderr = "fatal: branch not found"
        return dummy
    monkeypatch.setattr("dev_tools.git_tools.git_tool.subprocess.run", fake_run_branch_fail)
    with pytest.raises(SystemExit):
        check_branch_exists("nonexistent")

def test_generate_commit_overview(monkeypatch, capsys):
    # Patch subprocess.run in our module to simulate output for both summary and graph.
    monkeypatch.setattr("dev_tools.git_tools.git_tool.subprocess.run", fake_run_success)
    generate_commit_overview(start_date="01-04-2025", end_date="02-04-2025", author="John Doe", branch="develop")
    captured = capsys.readouterr().out
    assert "Total commits: 2" in captured
    assert "John Doe" in captured
    assert "* abc123 | Commit 1" in captured
