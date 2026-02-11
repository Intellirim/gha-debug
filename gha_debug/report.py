"""HTML report generator for gha-debug validation results."""

import os
import tempfile
from datetime import datetime, timezone


def _base_style():
    return """
    :root {
        --bg: #0d1117; --card: #161b22; --border: #30363d;
        --text: #e6edf3; --muted: #8b949e;
        --green: #3fb950; --red: #f85149; --blue: #58a6ff;
        --purple: #bc8cff; --orange: #d29922;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
        font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
        background:var(--bg); color:var(--text); line-height:1.6;
        padding:2rem; max-width:1100px; margin:0 auto;
    }
    .header { text-align:center; margin-bottom:2rem; padding-bottom:1.5rem; border-bottom:1px solid var(--border); }
    .header h1 { font-size:1.8rem; margin-bottom:0.3rem; }
    .header .subtitle { color:var(--muted); font-size:0.95rem; }
    .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin-bottom:2rem; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:1.2rem; }
    .card .label { color:var(--muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.3rem; }
    .card .value { font-size:1.5rem; font-weight:600; }
    .card .value.pass { color:var(--green); }
    .card .value.fail { color:var(--red); }
    .section { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:1.5rem; margin-bottom:1.5rem; }
    .section h2 { font-size:1.1rem; margin-bottom:1rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border); }
    .mono { font-family:'SF Mono',Monaco,Consolas,monospace; font-size:0.82rem; }
    .badge { display:inline-block; padding:0.15rem 0.5rem; border-radius:4px; font-size:0.72rem; font-weight:500; }
    .badge-ok { background:rgba(63,185,80,0.15); color:var(--green); }
    .badge-err { background:rgba(248,81,73,0.15); color:var(--red); }
    .badge-step { background:rgba(88,166,255,0.15); color:var(--blue); }
    .badge-action { background:rgba(188,140,255,0.15); color:var(--purple); }
    .job-card { background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:1rem; margin-bottom:0.8rem; }
    .job-title { font-weight:600; margin-bottom:0.5rem; }
    .step-list { list-style:none; padding:0; }
    .step-list li { padding:0.3rem 0; padding-left:1.5rem; position:relative; }
    .step-list li::before { content:''; position:absolute; left:0.3rem; top:0.65rem; width:8px; height:8px; border-radius:50%; background:var(--blue); }
    .step-list li.action::before { background:var(--purple); }
    .footer { text-align:center; color:var(--muted); font-size:0.8rem; margin-top:2rem; padding-top:1rem; border-top:1px solid var(--border); }
    .footer a { color:var(--blue); text-decoration:none; }
    .error-item { padding:0.5rem 0.8rem; margin:0.3rem 0; background:rgba(248,81,73,0.08); border-left:3px solid var(--red); border-radius:0 4px 4px 0; }
    """


def generate_html(workflow_results):
    """Generate HTML report for workflow validation.

    Args:
        workflow_results: List of dicts with keys:
            - file: str (workflow file path)
            - name: str (workflow name)
            - valid: bool
            - errors: list[str]
            - jobs: list of {name, runs_on, steps: [{name, uses, run}]}
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total_files = len(workflow_results)
    valid_count = sum(1 for w in workflow_results if w["valid"])
    error_count = sum(len(w["errors"]) for w in workflow_results)
    total_jobs = sum(len(w.get("jobs", [])) for w in workflow_results)
    total_steps = sum(len(j.get("steps", [])) for w in workflow_results for j in w.get("jobs", []))

    all_valid = valid_count == total_files
    status = "ALL VALID" if all_valid else f"{total_files - valid_count} FAILED"
    status_class = "pass" if all_valid else "fail"

    # Build workflow sections
    workflows_html = ""
    for wf in workflow_results:
        icon = "<span style='color:var(--green)'>&#10004;</span>" if wf["valid"] else "<span style='color:var(--red)'>&#10008;</span>"

        errors_html = ""
        if wf["errors"]:
            errors_html = "<div style='margin-top:0.8rem'>"
            for err in wf["errors"]:
                errors_html += f'<div class="error-item">{err}</div>'
            errors_html += "</div>"

        jobs_html = ""
        for job in wf.get("jobs", []):
            steps_html = ""
            for step in job.get("steps", []):
                if step.get("uses"):
                    steps_html += f'<li class="action"><span class="badge badge-action">action</span> <span class="mono">{step["uses"]}</span></li>'
                elif step.get("run"):
                    cmd = step["run"][:80]
                    steps_html += f'<li><span class="badge badge-step">run</span> <span class="mono">{cmd}</span></li>'

            jobs_html += f"""
            <div class="job-card">
                <div class="job-title">{job["name"]} <span style="color:var(--muted); font-weight:normal; font-size:0.85rem;">({job.get("runs_on", "?")})</span></div>
                <ul class="step-list">{steps_html}</ul>
            </div>"""

        workflows_html += f"""
        <div class="section">
            <h2>{icon} {wf["name"]} <span style="color:var(--muted); font-size:0.85rem; font-weight:normal;">({os.path.basename(wf["file"])})</span></h2>
            {errors_html}
            {jobs_html}
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>gha-debug Validation Report</title>
<style>{_base_style()}</style>
</head>
<body>

<div class="header">
    <h1>gha-debug Validation Report</h1>
    <div class="subtitle">GitHub Actions Workflow Analysis &mdash; {now}</div>
</div>

<div class="cards">
    <div class="card">
        <div class="label">Status</div>
        <div class="value {status_class}">{status}</div>
    </div>
    <div class="card">
        <div class="label">Workflows</div>
        <div class="value">{total_files}</div>
    </div>
    <div class="card">
        <div class="label">Jobs</div>
        <div class="value">{total_jobs}</div>
    </div>
    <div class="card">
        <div class="label">Steps</div>
        <div class="value">{total_steps}</div>
    </div>
</div>

{workflows_html}

<div class="footer">
    <p>Generated by <a href="https://pypi.org/project/gha-debug/">gha-debug</a> &mdash; GitHub Actions workflow debugger</p>
</div>

</body>
</html>"""
    return html


def export_html(workflow_results, output_path=None):
    """Generate and save HTML report, return file path."""
    html = generate_html(workflow_results)
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), "gha-debug-report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
