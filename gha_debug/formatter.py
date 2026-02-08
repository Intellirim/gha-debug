"""Output formatting with colors and tables."""

from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.table import Table

console = Console()


class Formatter:
    """Format output for the CLI with colors and structure."""

    def print_workflow_header(self, workflow_name: str, path: Path) -> None:
        """Print workflow header.

        Args:
            workflow_name: Name of the workflow
            path: Path to the workflow file
        """
        console.print(f"\n[bold cyan]Running workflow:[/bold cyan] {workflow_name}")
        console.print(f"[dim]File: {path}[/dim]")
        console.rule()

    def print_step_success(self, step_name: str, elapsed: float) -> None:
        """Print successful step.

        Args:
            step_name: Name of the step
            elapsed: Time elapsed in seconds
        """
        console.print(f"  [green]✓[/green] {step_name} [dim]({elapsed:.1f}s)[/dim]")

    def print_step_failure(self, step_name: str, elapsed: float) -> None:
        """Print failed step.

        Args:
            step_name: Name of the step
            elapsed: Time elapsed in seconds
        """
        console.print(f"  [red]✗[/red] {step_name} [dim]({elapsed:.1f}s)[/dim]")

    def print_success(self, total_time: float) -> None:
        """Print workflow success message.

        Args:
            total_time: Total execution time in seconds
        """
        console.print(f"\n[green]✓ Workflow completed successfully in {total_time:.1f}s[/green]")

    def print_failure(self, error: str) -> None:
        """Print workflow failure message.

        Args:
            error: Error message
        """
        console.print(f"\n[red]✗ Workflow failed: {error}[/red]")

    def print_workflow_structure(self, workflow: Dict[str, Any], path: Path) -> None:
        """Print workflow structure with jobs and steps.

        Args:
            workflow: Parsed workflow dictionary
            path: Path to the workflow file
        """
        console.print(f"[bold]{workflow['name']}[/bold] [dim]({path.name})[/dim]")

        for job in workflow["jobs"]:
            console.print(f"  [cyan]Job:[/cyan] {job['name']} [dim](runs-on: {job['runs-on']})[/dim]")

            for step in job["steps"]:
                icon = "🔧" if step.get("uses") else "▶"
                console.print(f"    {icon} {step['name']}")

    def print_environment(self, workflow: Dict[str, Any], job_filter: Optional[str] = None) -> None:
        """Print environment variables for workflow or job.

        Args:
            workflow: Parsed workflow dictionary
            job_filter: Optional job ID to filter by
        """
        table = Table(title="Environment Variables")
        table.add_column("Scope", style="cyan")
        table.add_column("Variable", style="green")
        table.add_column("Value", style="yellow")

        for key, value in workflow.get("env", {}).items():
            table.add_row("Workflow", key, str(value))

        for job in workflow["jobs"]:
            if job_filter and job["id"] != job_filter:
                continue

            for key, value in job.get("env", {}).items():
                table.add_row(f"Job: {job['id']}", key, str(value))

        table.add_row("Default", "CI", "true")
        table.add_row("Default", "GITHUB_ACTIONS", "true")
        table.add_row("Default", "GITHUB_WORKFLOW", workflow["name"])

        console.print(table)
