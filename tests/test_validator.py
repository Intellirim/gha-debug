"""Unit tests for validation logic."""

import tempfile
from pathlib import Path

from gha_debug.validator import WorkflowValidator


def test_validate_valid_workflow():
    """Test validation of a valid workflow."""
    workflow_yaml = """
name: Valid Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "Hello"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        validator = WorkflowValidator()
        errors = validator.validate(temp_path)
        assert len(errors) == 0
        assert isinstance(errors, list)
    finally:
        temp_path.unlink()


def test_validate_missing_jobs():
    """Test validation of workflow without jobs."""
    workflow_yaml = """
name: Invalid Workflow
on: [push]
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        validator = WorkflowValidator()
        errors = validator.validate(temp_path)
        assert any("jobs" in error.lower() for error in errors)
        assert len(errors) > 0
    finally:
        temp_path.unlink()


def test_validate_missing_steps():
    """Test validation of job without steps."""
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
        validator = WorkflowValidator()
        errors = validator.validate(temp_path)
        assert any("steps" in error.lower() for error in errors)
        assert len(errors) > 0
    finally:
        temp_path.unlink()


def test_validate_step_without_action_or_run():
    """Test validation of step without uses or run."""
    workflow_yaml = """
name: Invalid Workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Invalid step
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(workflow_yaml)
        temp_path = Path(f.name)

    try:
        validator = WorkflowValidator()
        errors = validator.validate(temp_path)
        assert any("uses" in error and "run" in error for error in errors)
        assert len(errors) > 0
    finally:
        temp_path.unlink()


def test_validate_invalid_yaml():
    """Test validation of invalid YAML syntax."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("invalid: [yaml")
        temp_path = Path(f.name)

    try:
        validator = WorkflowValidator()
        errors = validator.validate(temp_path)
        assert any("yaml" in error.lower() for error in errors)
        assert len(errors) > 0
    finally:
        temp_path.unlink()
