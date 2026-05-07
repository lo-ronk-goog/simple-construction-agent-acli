# agents-cli-demo

## 🏗️ About This Agent

This repository contains a **Remodel Material Estimator** agent, a precise construction estimator that helps users calculate materials needed for their projects.

### Key Features:
*   **Material Calculations**: Calculates quantities for subway tile, grout, paint, and hardwood flooring.
*   **Web Scraping**: Reads product URLs to find pricing or coverage info.
*   **MCP BigQuery Integration**: Talks to a **Model Context Protocol (MCP)** server to execute SQL queries against BigQuery to check live inventory in the `construction_inventory` dataset.

Agent generated with `agents-cli` version `0.1.3`.

## Project Structure

```
agents-cli-demo/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   ├── agent_runtime_app.py    # Agent Runtime application logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |
| `agents-cli deploy`  | Deploy agent to Agent Runtime                                                                |
| `agents-cli publish gemini-enterprise` | Register deployed agent to Gemini Enterprise                    |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## 🚀 CI/CD Pipeline

This project includes a custom CI/CD pipeline configured for GitHub Actions that follows enterprise best practices:

- **File**: `.github/workflows/ci.yml`
- **Environment**: Uses a shared Docker image in Artifact Registry for fast execution and to bypass local workstation blocks.

### Workflow Strategy:

1.  **Active Development (`dev` branch)**:
    *   Pushes to the `dev` branch trigger the **Continuous Integration** job.
    *   It runs unit tests and agent evaluations (`agents-cli eval run`) inside the container.
    *   Logs are kept quiet on success to reduce noise.
    *   Deployment is skipped.

2.  **Release to Production (`main` branch)**:
    *   When code is ready, merge `dev` into `main`.
    *   The merge triggers the workflow on the `main` branch.
    *   It runs the tests one last time.
    *   It features a **Human-in-the-Loop (HITL)** approval gate that pauses execution and waits for manual approval in the GitHub UI.
    *   Once approved, it:
        *   Finds the latest Git tag in history to use as the version.
        *   Updates `pyproject.toml` with the tag name.
        *   Mocks `gcloud` to force deployment to `us-central1` in project `lpr-gemini-enterprise-1`.
        *   Runs `agents-cli deploy` and `agents-cli publish gemini-enterprise` to fully register the agent!

### How to Release:
1.  Work on `dev`.
2.  When happy, create a tag on the `dev` branch (e.g., `v0.5.0`).
3.  Merge `dev` into `main`.
4.  Approve the deployment in the GitHub Actions UI!

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
