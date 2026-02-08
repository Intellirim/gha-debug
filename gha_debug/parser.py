"""YAML parsing logic for GitHub Actions workflows."""

from pathlib import Path
from typing import Any, Dict, List

import yaml


class WorkflowParser:
    """Parse GitHub Actions workflow YAML files."""

    def __init__(self, workflow_path: Path):
        """Initialize the parser with a workflow file path.

        Args:
            workflow_path: Path to the workflow YAML file
        """
        self.workflow_path = workflow_path

    def parse(self) -> Dict[str, Any]:
        """Parse the workflow file and extract structure.

        Returns:
            Dictionary containing workflow structure with jobs and steps

        Raises:
            ValueError: If the workflow file is invalid
            FileNotFoundError: If the workflow file doesn't exist
        """
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_path}")

        try:
            with open(self.workflow_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in workflow file: {e}")

        if not isinstance(data, dict):
            raise ValueError("Workflow file must contain a YAML dictionary")

        workflow_name = data.get("name", self.workflow_path.stem)
        jobs = data.get("jobs", {})
        env = data.get("env", {})

        parsed_jobs = []
        for job_id, job_data in jobs.items():
            if not isinstance(job_data, dict):
                continue

            steps = job_data.get("steps", [])
            parsed_steps = []

            for step in steps:
                if not isinstance(step, dict):
                    continue

                step_name = step.get("name", step.get("uses", step.get("run", "Unnamed step")))
                parsed_steps.append({
                    "name": step_name,
                    "uses": step.get("uses"),
                    "run": step.get("run"),
                    "env": step.get("env", {}),
                    "with": step.get("with", {}),
                })

            parsed_jobs.append({
                "id": job_id,
                "name": job_data.get("name", job_id),
                "runs-on": job_data.get("runs-on", "ubuntu-latest"),
                "env": job_data.get("env", {}),
                "steps": parsed_steps,
            })

        return {
            "name": workflow_name,
            "env": env,
            "jobs": parsed_jobs,
        }

    def get_job(self, workflow: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Get a specific job from the workflow.

        Args:
            workflow: Parsed workflow dictionary
            job_id: ID of the job to retrieve

        Returns:
            Job dictionary

        Raises:
            ValueError: If job not found
        """
        for job in workflow["jobs"]:
            if job["id"] == job_id:
                return job
        raise ValueError(f"Job '{job_id}' not found in workflow")
