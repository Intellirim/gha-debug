"""Local execution engine for workflow steps."""

import os
import subprocess
import time
from typing import Any, Dict, List, Optional

from rich.console import Console

from gha_debug.formatter import Formatter

console = Console()


class WorkflowRunner:
    """Run workflow steps locally with simulated GitHub Actions environment."""

    def __init__(self, workflow: Dict[str, Any], verbose: bool = False):
        """Initialize the runner with a parsed workflow.

        Args:
            workflow: Parsed workflow dictionary
            verbose: Whether to show verbose output
        """
        self.workflow = workflow
        self.verbose = verbose
        self.formatter = Formatter()

    def run(self, job_filter: Optional[str] = None) -> Dict[str, Any]:
        """Run the workflow or a specific job.

        Args:
            job_filter: Optional job ID to run only that job

        Returns:
            Dictionary with success status and timing information
        """
        start_time = time.time()

        jobs_to_run = self.workflow["jobs"]
        if job_filter:
            jobs_to_run = [j for j in jobs_to_run if j["id"] == job_filter]
            if not jobs_to_run:
                return {
                    "success": False,
                    "error": f"Job '{job_filter}' not found",
                    "total_time": 0,
                }

        for job in jobs_to_run:
            success = self._run_job(job)
            if not success:
                total_time = time.time() - start_time
                return {
                    "success": False,
                    "error": f"Job '{job['id']}' failed",
                    "total_time": total_time,
                }

        total_time = time.time() - start_time
        return {
            "success": True,
            "total_time": total_time,
        }

    def _run_job(self, job: Dict[str, Any]) -> bool:
        """Run a single job.

        Args:
            job: Job dictionary

        Returns:
            True if job succeeded, False otherwise
        """
        console.print(f"\n[bold]Job:[/bold] {job['name']}")

        env = self._build_environment(job)

        for step in job["steps"]:
            success = self._run_step(step, env)
            if not success:
                return False

        return True

    def _run_step(self, step: Dict[str, Any], env: Dict[str, str]) -> bool:
        """Run a single step.

        Args:
            step: Step dictionary
            env: Environment variables

        Returns:
            True if step succeeded, False otherwise
        """
        start_time = time.time()

        step_env = {**env, **step.get("env", {})}

        if step.get("uses"):
            success = self._run_action(step, step_env)
        elif step.get("run"):
            success = self._run_command(step, step_env)
        else:
            success = True

        elapsed = time.time() - start_time

        if success:
            self.formatter.print_step_success(step["name"], elapsed)
        else:
            self.formatter.print_step_failure(step["name"], elapsed)

        return success

    def _run_action(self, step: Dict[str, Any], env: Dict[str, str]) -> bool:
        """Simulate running a GitHub Action.

        Args:
            step: Step dictionary
            env: Environment variables

        Returns:
            True (actions are simulated as successful)
        """
        action = step["uses"]

        if self.verbose:
            console.print(f"  [dim]Using action: {action}[/dim]")
            if step.get("with"):
                console.print(f"  [dim]With: {step['with']}[/dim]")

        time.sleep(0.1)
        return True

    def _run_command(self, step: Dict[str, Any], env: Dict[str, str]) -> bool:
        """Run a shell command.

        Args:
            step: Step dictionary
            env: Environment variables

        Returns:
            True if command succeeded, False otherwise
        """
        command = step["run"]

        if self.verbose:
            console.print(f"  [dim]Running: {command}[/dim]")

        try:
            result = subprocess.run(
                command,
                shell=True,
                env={**os.environ.copy(), **env},
                capture_output=not self.verbose,
                text=True,
            )

            if result.returncode == 0:
                return True
            else:
                if not self.verbose and result.stderr:
                    console.print(f"  [red]{result.stderr.strip()}[/red]")
                return False
        except Exception as e:
            console.print(f"  [red]Error: {str(e)}[/red]")
            return False

    def _build_environment(self, job: Dict[str, Any]) -> Dict[str, str]:
        """Build environment variables for a job.

        Args:
            job: Job dictionary

        Returns:
            Dictionary of environment variables
        """
        env = {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_WORKFLOW": self.workflow["name"],
            "GITHUB_JOB": job["id"],
            "GITHUB_RUNNER_OS": "Linux",
            "RUNNER_OS": "Linux",
        }

        env.update(self.workflow.get("env", {}))
        env.update(job.get("env", {}))

        return {k: str(v) for k, v in env.items()}
