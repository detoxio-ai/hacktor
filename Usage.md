# Hacktor Usage Guide

Hacktor is a tool designed for automated security testing of web applications, leveraging AI capabilities to enhance the effectiveness and depth of tests. This guide will walk you through the process of installing, setting up, and using Hacktor.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python (preferably Python 3.x)
- Git
- Poetry (a dependency management tool for Python)

## Installation

### Step 1: Clone the Hacktor Repository

Begin by cloning the Hacktor repository from GitHub:

```bash
git clone https://github.com/detoxio-ai/hacktor
```

Navigate into the cloned directory:

```bash
cd hacktor/
```

### Step 2: Install Poetry

If you haven't installed Poetry yet, you can do so with the following commands:

```bash
pip3 install poetry
```

To ensure Poetry is accessible from the command line, add it to your system's `PATH`:

```bash
export PATH=$PATH:$HOME/.local/bin/poetry
```

### Step 3: Install Dependencies

Once inside the Hacktor directory, install the necessary dependencies:

```bash
poetry install
```

## Running Hacktor

### Step 4: Configuration

Before running Hacktor, you'll need to configure your environment with the necessary API key and host details. These details should be stored securely in a key file (e.g., `~/.mydetoxio.uat.key`):


```bash
export DETOXIO_API_KEY=xxxxx
```

Optionally if you are using UAT:
```bash
export DETOXIO_API_HOST=api-uat.detoxio.ai
```


### Step 5: Running Hacktor

Hacktor can be run to test web applications with specific options:

```bash
poetry run hacktor webapps <target_url> --use_ai --max_crawling_steps 10 --no_of_tests 10 --json report.json --markdown report.md -v
```

Replace `<target_url>` with the URL of the web application you wish to test.

#### Command Options:
- `--use_ai`: Enables AI features for more advanced testing.
- `--max_crawling_steps`: Specifies the maximum number of crawling steps.
- `--no_of_tests`: Determines the number of tests to run.
- `--json report.json`: Outputs the results in JSON format.
- `--markdown report.md`: Outputs the results in Markdown format.
- `-v`: Enables verbose mode.

### Step 6: Review the Reports

After the tests complete, you can review the generated reports:

- **Markdown Report:**

  ```bash
  vim report.md
  ```

- **JSON Report:**

  ```bash
  cat report.json | jq . | more
  ```

### Step 7: Running Hacktor with Attack Module

Hacktor also allows you to specify a particular attack module for more targeted testing. To do so, you can use the `--attack_module` option followed by the module's name, such as `OWASP-LLM-APP`. Here's an example:

```bash
poetry run hacktor webapps <target_url> --use_ai --max_crawling_steps 10 --no_of_tests 10 --attack_module OWASP-LLM-APP --json report.json --markdown report.md -v
```

In this command, we are specifying `OWASP-LLM-APP` as the attack module, which focuses on testing vulnerabilities based on OWASP's LLM (Large Language Model) security guidelines.

#### Command Options:
- `--attack_module <module>`: Specifies the attack module to use, such as `OWASP-LLM-APP`.
- Other options remain the same as described in Step 5.

## Updating Hacktor

To update Hacktor to the latest version, navigate to the Hacktor directory and pull the latest changes:

```bash
git pull origin main
poetry install
```

## Additional Commands

For more detailed usage options, you can view the help documentation:

```bash
poetry run hacktor webapps -h
```

