"""Unit tests for CLI interface."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from gha_debug.cli import cli


def test_cli_version():
    """Test CLI version option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_help():
    """Test CLI help option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Debug GitHub Actions" in result.output


def test_run_command():
    """Test run command with valid workflow."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["run", str(temp_path)])

        assert result.exit_code == 0
        assert "Test Workflow" in result.output or "OK" in result.output
    finally:
        temp_path.unlink()


def test_run_command_with_job_filter():
    """Test run command with specific job."""
    workflow_yaml = """
name: Multi-job Workflow
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "build"
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["run", str(temp_path), "--job", "test"])

        assert result.exit_code == 0
        assert "Multi-job Workflow" in result.output or "OK" in result.output
    finally:
        temp_path.unlink()


def test_run_command_verbose():
    """Test run command with verbose flag."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "verbose test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["run", str(temp_path), "--verbose"])

        assert result.exit_code == 0
        assert "Test Workflow" in result.output or "OK" in result.output
    finally:
        temp_path.unlink()


def test_list_command():
    """Test list command with workflow file."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["list", str(temp_path)])

        assert result.exit_code == 0
        assert "Test Workflow" in result.output
    finally:
        temp_path.unlink()


def test_list_command_directory():
    """Test list command with directory."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_file = Path(temp_dir) / "test.yml"
        workflow_file.write_text(workflow_yaml)

        runner = CliRunner()
        result = runner.invoke(cli, ["list", temp_dir])

        assert result.exit_code == 0
        assert "Test Workflow" in result.output or "test.yml" in result.output


def test_env_command():
    """Test env command."""
    workflow_yaml = """
name: Test Workflow
env:
  GLOBAL_VAR: global_value
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      JOB_VAR: job_value
    steps:
      - run: echo "test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["env", str(temp_path)])

        assert result.exit_code == 0
        assert "GLOBAL_VAR" in result.output or "Environment" in result.output
    finally:
        temp_path.unlink()


def test_validate_command_valid():
    """Test validate command with valid workflow."""
    workflow_yaml = """
name: Valid Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(temp_path)])

        assert result.exit_code == 0
        assert "OK" in result.output or "valid" in result.output.lower()
    finally:
        temp_path.unlink()


def test_validate_command_invalid():
    """Test validate command with invalid workflow."""
    workflow_yaml = """
name: Invalid Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(temp_path)])

        assert result.exit_code == 1
        assert "steps" in result.output.lower() or "error" in result.output.lower()
    finally:
        temp_path.unlink()
