"""Workflow validation logic."""

from pathlib import Path
from typing import List

import yaml


class WorkflowValidator:
    """Validate GitHub Actions workflow files."""

    def validate(self, workflow_path: Path) -> List[str]:
        """Validate a workflow file and return list of errors.

        Args:
            workflow_path: Path to the workflow YAML file

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not workflow_path.exists():
            return [f"File not found: {workflow_path}"]

        # Read raw content for syntax checks
        with open(workflow_path, "r") as f:
            raw_content = f.read()

        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as e:
            return [f"Invalid YAML syntax: {e}"]

        if not isinstance(data, dict):
            return ["Workflow must be a YAML dictionary"]

        if "jobs" not in data:
            errors.append("Missing required field: 'jobs'")
            return errors

        if not isinstance(data["jobs"], dict):
            errors.append("'jobs' must be a dictionary")
            return errors

        if not data["jobs"]:
            errors.append("Workflow must have at least one job")

        for job_id, job_data in data["jobs"].items():
            if not isinstance(job_data, dict):
                errors.append(f"Job '{job_id}' must be a dictionary")
                continue

            if "steps" not in job_data:
                errors.append(f"Job '{job_id}' missing required field: 'steps'")
                continue

            if not isinstance(job_data["steps"], list):
                errors.append(f"Job '{job_id}': 'steps' must be a list")
                continue

            if not job_data["steps"]:
                errors.append(f"Job '{job_id}' must have at least one step")

            for idx, step in enumerate(job_data["steps"]):
                if not isinstance(step, dict):
                    errors.append(f"Job '{job_id}', step {idx}: must be a dictionary")
                    continue

                has_uses = "uses" in step
                has_run = "run" in step

                if not has_uses and not has_run:
                    errors.append(f"Job '{job_id}', step {idx}: must have 'uses' or 'run'")

                if has_uses and has_run:
                    errors.append(f"Job '{job_id}', step {idx}: cannot have both 'uses' and 'run'")

        self._validate_syntax_patterns(raw_content, data, errors)

        return errors

    def _validate_syntax_patterns(self, raw_content: str, data: dict, errors: List[str]) -> None:
        """Check for common syntax mistakes.

        Args:
            raw_content: Raw YAML content as string
            data: Parsed workflow YAML
            errors: List to append errors to
        """
        # Check for malformed GitHub expressions (no space)
        if "${{}}" in raw_content:
            errors.append("Syntax hint: GitHub expressions use '${{ }}' not '${{}}'")

        if "on" not in data and True not in data:
            errors.append("Warning: Missing 'on:' trigger configuration")
