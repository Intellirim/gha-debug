"""CLI interface for gha-debug."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from gha_debug import __version__
from gha_debug.formatter import Formatter
from gha_debug.parser import WorkflowParser
from gha_debug.runner import WorkflowRunner
from gha_debug.validator import WorkflowValidator

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Debug GitHub Actions workflows locally with step-by-step execution."""
    pass


@cli.command()
@click.argument("workflow_path", type=click.Path(exists=True))
@click.option("--job", "-j", help="Specific job to run")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def run(workflow_path: str, job: Optional[str], verbose: bool) -> None:
    """Run a GitHub Actions workflow locally."""
    try:
        path = Path(workflow_path)
        parser = WorkflowParser(path)
        workflow = parser.parse()

        runner = WorkflowRunner(workflow, verbose=verbose)
        formatter = Formatter()

        formatter.print_workflow_header(workflow["name"], path)

        result = runner.run(job_filter=job)

        if result["success"]:
            formatter.print_success(result["total_time"])
            sys.exit(0)
        else:
            formatter.print_failure(result["error"])
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("workflow_path", type=click.Path(exists=False), default=".github/workflows")
def list(workflow_path: str) -> None:
    """List all workflows, jobs, and steps."""
    try:
        path = Path(workflow_path)

        if path.is_file():
            workflow_files = [path]
        elif path.is_dir():
            workflow_files = list(path.glob("*.yml")) + list(path.glob("*.yaml"))
        else:
            console.print(f"[yellow]Warning:[/yellow] Path not found: {workflow_path}")
            sys.exit(1)

        if not workflow_files:
            console.print("[yellow]No workflow files found[/yellow]")
            sys.exit(0)

        formatter = Formatter()

        for wf_path in sorted(workflow_files):
            parser = WorkflowParser(wf_path)
            workflow = parser.parse()
            formatter.print_workflow_structure(workflow, wf_path)
            console.print()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("workflow_path", type=click.Path(exists=True))
@click.option("--job", "-j", help="Specific job to show environment for")
def env(workflow_path: str, job: Optional[str]) -> None:
    """Display environment variables and contexts for a workflow."""
    try:
        path = Path(workflow_path)
        parser = WorkflowParser(path)
        workflow = parser.parse()

        formatter = Formatter()
        formatter.print_environment(workflow, job_filter=job)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("workflow_paths", nargs=-1, type=click.Path(exists=True), required=True)
def validate(workflow_paths: tuple) -> None:
    """Validate workflow syntax and catch common errors."""
    try:
        validator = WorkflowValidator()
        all_valid = True

        for workflow_path in workflow_paths:
            path = Path(workflow_path)

            if path.is_dir():
                files = list(path.glob("*.yml")) + list(path.glob("*.yaml"))
            else:
                files = [path]

            for file_path in files:
                errors = validator.validate(file_path)

                if errors:
                    all_valid = False
                    console.print(f"\n[red]✗[/red] {file_path}")
                    for error in errors:
                        console.print(f"  [red]•[/red] {error}")
                else:
                    console.print(f"[green]✓[/green] {file_path}")

        if all_valid:
            console.print("\n[green]All workflows are valid![/green]")
            sys.exit(0)
        else:
            console.print("\n[red]Some workflows have errors[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
