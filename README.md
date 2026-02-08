# gha-debug

Debug GitHub Actions workflows locally with step-by-step execution

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`gha-debug` is a lightweight CLI tool that helps developers test and debug GitHub Actions workflows locally before pushing to CI. Unlike heavy Docker-based solutions, it provides fast validation, clear step-by-step execution visibility, and helpful error messages.

## Installation

```bash
pip install gha-debug
```

## Usage

### Run a workflow locally

```bash
gha-debug run .github/workflows/test.yml
```

### Run a specific job with verbose output

```bash
gha-debug run .github/workflows/build.yml --job build --verbose
```

### List all workflows and jobs

```bash
gha-debug list
```

### Show environment variables for a job

```bash
gha-debug env .github/workflows/deploy.yml --job deploy
```

### Validate workflow syntax

```bash
gha-debug validate .github/workflows/*.yml
```

## Features

- ✅ Parse and validate GitHub Actions workflow YAML files
- ✅ List all workflows, jobs, and steps with clear formatting
- ✅ Run workflows locally with simulated GitHub Actions environment
- ✅ Show detailed step-by-step execution with timing information
- ✅ Display environment variables and contexts for debugging
- ✅ Validate workflow syntax and catch common errors before pushing
- ✅ Colorized output for better readability
- ✅ Support for filtering by specific job within a workflow

## Why gha-debug?

Debugging GitHub Actions workflows is painful:
- Logs are hard to navigate in the web interface
- Re-running failed jobs wastes time
- No simple local testing that mirrors the CI environment

`gha-debug` solves this by providing a fast feedback loop. It doesn't try to perfectly replicate GitHub's environment (which causes compatibility issues), but instead focuses on what developers need most: quick validation and clear error messages.

## Example Output

```
$ gha-debug run .github/workflows/test.yml

Running workflow: test.yml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Job: test
  ✓ Checkout code (1.2s)
  ✓ Setup Python 3.11 (0.8s)
  ✓ Install dependencies (4.5s)
  ✓ Run tests (12.3s)

✓ Workflow completed successfully in 18.8s
```

## License

MIT License - Copyright (c) 2026 Intellirim
