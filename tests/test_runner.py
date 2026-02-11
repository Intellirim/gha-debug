"""Unit tests for workflow runner."""

import tempfile
from pathlib import Path

from gha_debug.parser import WorkflowParser
from gha_debug.runner import WorkflowRunner


def test_run_workflow_success():
    """Test running a successful workflow."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Echo test
        run: echo "test"
      - name: True command
        run: "true"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=False)

        result = runner.run()

        assert result["success"] is True
        assert result["total_time"] >= 0
    finally:
        temp_path.unlink()


def test_run_workflow_failure():
    """Test running a workflow with failing step."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Failing command
        run: exit 1
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=False)

        result = runner.run()

        assert result["success"] is False
        assert "error" in result
        assert result["total_time"] >= 0
    finally:
        temp_path.unlink()


def test_run_specific_job():
    """Test running a specific job by ID."""
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
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=False)

        result = runner.run(job_filter="test")

        assert result["success"] is True
        assert result["total_time"] >= 0
    finally:
        temp_path.unlink()


def test_run_nonexistent_job():
    """Test running a job that doesn't exist."""
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
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=False)

        result = runner.run(job_filter="nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]
        assert result["total_time"] == 0
    finally:
        temp_path.unlink()


def test_run_action_step():
    """Test running a step with uses (action)."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 1
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=True)

        result = runner.run()

        assert result["success"] is True
        assert result["total_time"] >= 0
    finally:
        temp_path.unlink()


def test_environment_variables():
    """Test environment variable handling."""
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
      - name: Check env
        run: test "$GLOBAL_VAR" = "global_value"
        env:
          STEP_VAR: step_value
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner = WorkflowRunner(workflow, verbose=False)

        result = runner.run()

        assert result["success"] is True
        assert result["total_time"] >= 0
    finally:
        temp_path.unlink()


def test_verbose_output():
    """Test verbose mode with actions and commands."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "verbose test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        runner_verbose = WorkflowRunner(workflow, verbose=True)
        runner_quiet = WorkflowRunner(workflow, verbose=False)

        result_verbose = runner_verbose.run()
        result_quiet = runner_quiet.run()

        assert result_verbose["success"] is True
        assert result_quiet["success"] is True
    finally:
        temp_path.unlink()
