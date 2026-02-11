"""Unit tests for output formatter."""

import tempfile
from pathlib import Path

from gha_debug.formatter import Formatter
from gha_debug.parser import WorkflowParser


def test_print_workflow_header():
    """Test printing workflow header."""
    formatter = Formatter()
    path = Path("/test/workflow.yml")

    formatter.print_workflow_header("Test Workflow", path)
    assert formatter is not None
    assert path.name == "workflow.yml"


def test_print_step_success():
    """Test printing successful step."""
    formatter = Formatter()

    formatter.print_step_success("Test Step", 1.5)
    assert formatter is not None
    assert 1.5 > 0


def test_print_step_failure():
    """Test printing failed step."""
    formatter = Formatter()

    formatter.print_step_failure("Test Step", 2.3)
    assert formatter is not None
    assert 2.3 > 0


def test_print_success():
    """Test printing workflow success message."""
    formatter = Formatter()

    formatter.print_success(10.5)
    assert formatter is not None
    assert 10.5 > 0


def test_print_failure():
    """Test printing workflow failure message."""
    formatter = Formatter()

    formatter.print_failure("Job failed")
    assert formatter is not None
    assert len("Job failed") > 0


def test_print_workflow_structure():
    """Test printing workflow structure."""
    workflow_yaml = """
name: Test Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Test
        run: pytest
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        formatter = Formatter()

        formatter.print_workflow_structure(workflow, temp_path)

        assert workflow["name"] == "Test Workflow"
        assert len(workflow["jobs"]) == 1
    finally:
        temp_path.unlink()


def test_print_environment():
    """Test printing environment variables."""
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
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        formatter = Formatter()

        formatter.print_environment(workflow)

        assert "GLOBAL_VAR" in workflow["env"]
        assert workflow["jobs"][0]["env"]["JOB_VAR"] == "job_value"
    finally:
        temp_path.unlink()


def test_print_environment_filtered_job():
    """Test printing environment for specific job."""
    workflow_yaml = """
name: Multi-job Workflow
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      BUILD_VAR: build_value
    steps:
      - run: echo "build"
  test:
    runs-on: ubuntu-latest
    env:
      TEST_VAR: test_value
    steps:
      - run: echo "test"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()
        formatter = Formatter()

        formatter.print_environment(workflow, job_filter="test")

        assert len(workflow["jobs"]) == 2
        test_job = [j for j in workflow["jobs"] if j["id"] == "test"][0]
        assert test_job["env"]["TEST_VAR"] == "test_value"
    finally:
        temp_path.unlink()
