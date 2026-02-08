"""Unit tests for YAML parsing."""

import tempfile
from pathlib import Path

import pytest

from gha_debug.parser import WorkflowParser


def test_parse_valid_workflow():
    """Test parsing a valid workflow file."""
    workflow_yaml = """
name: Test Workflow
on: [push]
env:
  GLOBAL_VAR: global_value

jobs:
  test:
    name: Test Job
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Run tests
        run: pytest
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()

        assert workflow["name"] == "Test Workflow"
        assert "GLOBAL_VAR" in workflow["env"]
        assert len(workflow["jobs"]) == 1
        assert workflow["jobs"][0]["id"] == "test"
        assert len(workflow["jobs"][0]["steps"]) == 2
    finally:
        temp_path.unlink()


def test_parse_missing_file():
    """Test parsing a non-existent file."""
    parser = WorkflowParser(Path("/nonexistent/file.yml"))

    with pytest.raises(FileNotFoundError):
        parser.parse()


def test_parse_invalid_yaml():
    """Test parsing invalid YAML."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("invalid: yaml: content: [")
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        with pytest.raises(ValueError):
            parser.parse()
    finally:
        temp_path.unlink()


def test_get_job():
    """Test retrieving a specific job."""
    workflow_yaml = """
name: Multi-job Workflow
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo build
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        parser = WorkflowParser(temp_path)
        workflow = parser.parse()

        build_job = parser.get_job(workflow, "build")
        assert build_job["id"] == "build"

        with pytest.raises(ValueError):
            parser.get_job(workflow, "nonexistent")
    finally:
        temp_path.unlink()
