# AutoFullStack

## Overview

AutoFullStack is a multi-agent framework for generating full-stack management systems from natural language project requirements. Given a project name and description, it plans the project, generates backend and frontend code, and can place the generated project into an execution environment for build and runtime checks.

The framework is mainly designed for research on project-level software generation. It includes an incremental workflow, a waterfall-style baseline, and an incremental variant without self-refinement, so that different generation strategies can be compared under the same project scaffold and benchmark tasks.

## Repository Structure

```text
AutoFullStack/
|-- auto_full_stack/          # Core implementation of the framework
|   |-- workflows/            # Planning, development, operations, and baseline workflows
|   |-- workflows/agent/      # Agent roles used by the workflows
|   |-- workflows/prompt/     # Prompt templates for planning and code generation
|   |-- templates/            # Full-stack project scaffold and configuration templates
|   |-- common/               # Shared configuration, logging, workspace, and LLM utilities
|   |-- utils/                # File, database, Redis, prompt, and report utilities
|   |-- app.py                # Entry point for running a single project generation task
|   `-- benchmark_runner.py   # Batch runner for benchmark tasks
|-- data/                     # Benchmark task descriptions
|-- experiment_results/       # CSV files used for the reported experimental results
|-- .env.example              # Example environment configuration
|-- requirements.txt          # Python dependencies
`-- README.md
```

## Requirements

AutoFullStack was developed and tested with Python 3.10.18 in a Conda environment. To run the framework, the following software and services are required:

- Python 3.10
- An OpenAI-compatible LLM API endpoint
- Java 17
- Maven
- MySQL 8.x
- Redis

Java and Maven are required because the development workflow builds and tests the generated Spring Boot backend during code generation. MySQL is also used during generation: AutoFullStack creates project-specific databases, executes generated SQL scripts, and runs backend tests against the database. The default MySQL connection is `localhost:3306` with user `root` and password `root`, and the account must be allowed to create and drop databases. Redis is used to store workflow status, project namespaces, and process information. The default Redis connection is `localhost:6379` without a password.

Generated projects use a Spring Boot backend and a Vue 2 frontend. Running a generated project requires:

- Java 17 and Maven for the backend
- Node.js and npm compatible with Vue CLI 4 for the frontend
- MySQL and Redis services

By default, generated projects use backend port `8080`, frontend port `80`, MySQL port `3306`, and Redis port `6379`.

## Installation

Create a Python environment and install the required packages:

```bash
conda create -n AutoFullStack python=3.10
conda activate AutoFullStack
pip install -r requirements.txt
```

After installation, you can check whether the Python entry point is available:

```bash
python -m auto_full_stack.app --help
```

Make sure Java, Maven, MySQL, Redis, Node.js, and npm are also installed and available from the command line before running a full generation workflow.

## Configuration

Create a local environment file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set the LLM configuration:

```env
LLM_API_KEY="your-api-key"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="your-model-name"
```

`LLM_BASE_URL` can point to any OpenAI-compatible API endpoint. LangSmith variables in `.env.example` are optional and are only needed if you want to trace LangChain calls.

AutoFullStack currently assumes local MySQL and Redis services with the following defaults:

```text
MySQL: localhost:3306, user=root, password=root
Redis: localhost:6379, no password
```

The MySQL account must have permission to create and drop databases because each generated project uses its own project-specific database.

## Single Project Generation

Use `auto_full_stack.app` to run AutoFullStack on one project requirement:

```bash
python -m auto_full_stack.app \
  --project-name "Personal Contact Manager" \
  --description "Please help me create a personal contact management system. This system includes a contact management module. Contact management enables users to add, edit, delete and view contact information." \
  --approach incremental
```

The `--approach` option supports three workflow variants:

```text
incremental
incremental_no_self_refinement
waterfall
```

If no arguments are provided, the script runs a default example project with the `incremental` approach.

Generated files are written to:

```text
workspace/<project_namespace>/
```

The namespace is generated automatically from the project name. During a full run, AutoFullStack performs planning, code generation, backend verification, and operations steps. The operations step builds and starts the generated backend and frontend, so the process may keep running while the generated services are active.

## Generated Project Structure and Execution

### Generated Project Structure

By default, a generated project is written to:

```text
workspace/<project_namespace>/
```

The project namespace is generated automatically from the project name. A generated project has the following main structure:

```text
workspace/<project_namespace>/
|-- backend/       # Generated Spring Boot backend project
|-- frontend/      # Generated Vue 2 frontend project
|-- sql/           # Base SQL scripts and generated module SQL scripts
|-- resources/     # Planning and development artifacts
|-- logs/          # Runtime logs created by the operations workflow
|-- start.bat
`-- start.sh
```

The `backend/` directory contains a Maven-based Spring Boot project, and the `frontend/` directory contains a Vue 2 project built with Vue CLI. The `sql/` directory includes base initialization scripts such as `init.sql` and `quartz.sql`, together with generated SQL scripts for project-specific modules. The `resources/` directory stores intermediate artifacts produced during planning and development.

### Running a Generated Project

When `auto_full_stack.app` is run with a complete workflow, the operations step builds and starts the generated backend and frontend automatically. To run an already generated project manually, first make sure MySQL and Redis are running and that the project database has been initialized from the scripts in `sql/`.

For the backend:

```bash
cd workspace/<project_namespace>/backend
mvn clean test
mvn package -DskipTests
java -Dfile.encoding=UTF-8 -Dconsole.encoding=UTF-8 -jar admin/target/admin.jar
```

For the frontend:

```bash
cd workspace/<project_namespace>/frontend
npm install
npm run dev
```

The database name is the same as `<project_namespace>`. In a full AutoFullStack run, the workflow initializes the database and executes the SQL scripts automatically. If you move or rerun a generated project in a fresh environment, import the SQL scripts in `sql/`, including `quartz.sql`, `init.sql`, and the generated `create_tables_inc_*.sql` and `insert_menu_inc_*.sql` files.

By default, the backend runs at:

```text
http://localhost:8080
```

The frontend runs at:

```text
http://localhost:80
```

If port `80` is unavailable or requires elevated permissions, change the frontend port in `frontend/vue.config.js`.

## Benchmark Tasks and Batch Runner

The `data/` directory contains 30 benchmark tasks used for project-level full-stack generation:

```text
data/simple_dataset.json     # 10 simple tasks
data/medium_dataset.json     # 10 medium tasks
data/complex_dataset.json    # 10 complex tasks
```

Each task contains a project name and a natural language project description. These descriptions are used as inputs to AutoFullStack.

`auto_full_stack.benchmark_runner` runs benchmark tasks in batch mode. It supports the incremental workflow, the waterfall baseline, and the incremental workflow without self-refinement:

```text
incremental
incremental_no_self_refinement
waterfall
```

Run one simple task with the incremental workflow:

```bash
python -m auto_full_stack.benchmark_runner --approach incremental --complexity simple --limit 1
```

Run all tasks for one approach:

```bash
python -m auto_full_stack.benchmark_runner --approach incremental --complexity all
```

Run all approaches on all benchmark tasks:

```bash
python -m auto_full_stack.benchmark_runner --approach all --complexity all
```

Run a specific project by ID:

```bash
python -m auto_full_stack.benchmark_runner --approach incremental --complexity complex --project-id proj_complex_02
```

By default, generated benchmark projects are written under:

```text
experiments/<approach>/<complexity>/<project_namespace>/
```

This location can be changed with `--workspace-base`.

The batch runner writes summary CSV files to:

```text
experiment_results/
```

For unattended batch execution, `benchmark_runner.py` runs the planning and development stages and skips the operations workflow. This means it records generation statistics such as status, module-level verification results, token usage, elapsed time, and generated lines of code, but it does not automatically perform the final backend/frontend runtime check for every generated project.

## Experiment Results

The `experiment_results/` directory contains the CSV files used to summarize the experiments reported in the paper.

```text
experiment_results/
|-- benchmark_results_incremental_all_20260314_104325.csv
|-- benchmark_results_incremental_no_self_refinement_all_20260409_214202.csv
|-- benchmark_results_waterfall_all_20260318_165450.csv
|-- eval_e2e_executability.csv
|-- eval_functional_correctness.csv
```

The `benchmark_results_*.csv` files are produced by `benchmark_runner.py`. They record project-level generation statistics, including generation status, module verification summary, token usage, elapsed time, and generated lines of code for each workflow variant.

`eval_e2e_executability.csv` records backend and frontend build results for generated projects. It is used to summarize end-to-end executability at the project level.

`eval_functional_correctness.csv` records module-level functional scores. Each row corresponds to one generated module and contains a score from 0 to 5, together with evaluator notes.

These files are provided as experiment artifacts. Re-running the benchmark may produce different outputs because the framework depends on LLM generation, external API latency, and the local execution environment.

## Notes and Limitations

AutoFullStack is intended as a research prototype for project-level full-stack software generation. The generated code and benchmark results may vary across runs because the framework relies on LLM outputs, external API availability, and the local execution environment.

The current implementation assumes local MySQL and Redis services with default credentials and ports. These settings are convenient for controlled experiments but should be adjusted before using the generated projects in other environments.

The benchmark tasks mainly cover management-style full-stack applications based on a shared project scaffold. They are not intended to represent all possible software development scenarios.

## Acknowledgement

The project scaffold used by AutoFullStack is adapted from RuoYi-Vue, which is released under the MIT License. The original copyright and license notice are retained in accordance with the MIT License.
