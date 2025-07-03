## [Coral GitClone Agent](https://github.com/Coral-Protocol/Coral-GitClone-Agent)
 
The GitClone Agent helps you clone a specific repository to your local machine using the git clone command, check out the branch corresponding to a particular pull request, and lets you know the local project path—all by simply providing the repository name and PR number.

## Responsibility
The GitClone Agent automates repository cloning, branch checkout for pull requests, and provides local project paths, streamlining codebase setup for development and review

## Details
- **Framework**: CrewAI
- **Tools used**: Git CLI Tool, Coral Server Tools
- **AI model**: OpenAI GPT-4.1
- **Date added**: 02/05/25
- **License**: MIT

## Setup the Agent

### 1. Clone & Install Dependencies

<details>  

```bash
# In a new terminal clone the repository:
git clone https://github.com/Coral-Protocol/Coral-GitClone-Agent.git

# Navigate to the project directory:
cd Coral-GitClone-Agent

# Download and run the UV installer, setting the installation directory to the current one
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(pwd) sh

# Create a virtual environment named `.venv` using UV
uv venv .venv

# Activate the virtual environment
source .venv/bin/activate

# install uv
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```

</details>

### 2. Configure Environment Variables

Get the API Key:
[OpenAI](https://platform.openai.com/api-keys) or [GROQ](https://console.groq.com/keys)

<details>

```bash
# Create .env file in project root
cp -r .env.example .env
```
</details>

## Run the Agent

You can run in either of the below modes to get your system running.  

- The Executable Model is part of the Coral Protocol Orchestrator which works with [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio).  
- The Dev Mode allows the Coral Server and all agents to be seaprately running on each terminal without UI support.  

### 1. Executable Mode

Checkout: [How to Build a Multi-Agent System with Awesome Open Source Agents using Coral Protocol](https://github.com/Coral-Protocol/existing-agent-sessions-tutorial-private-temp) and update the file: `coral-server/src/main/resources/application.yaml` with the details below, then run the [Coral Server](https://github.com/Coral-Protocol/coral-server) and [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio). You do not need to set up the `.env` in the project directory for running in this mode; it will be captured through the variables below.

<details>

For Linux or MAC:

```bash
# PROJECT_DIR="/PATH/TO/YOUR/PROJECT"

applications:
  - id: "app"
    name: "Default Application"
    description: "Default application for testing"
    privacyKeys:
      - "default-key"
      - "public"
      - "priv"

registry:
  GitClone:
    options:
      - name: "API_KEY"
        type: "string"
        description: "API key for the service"
    runtime:
      type: "executable"
      command: ["bash", "-c", "${PROJECT_DIR}/run_agent.sh main.py"]
      environment:
        - name: "API_KEY"
          from: "API_KEY"
        - name: "MODEL_NAME"
          value: "openai/gpt-4.1-2025-04-14"
        - name: "MODEL_TOKEN"
          value: "16000"
        - name: "MODEL_TEMPERATURE"
          value: "0.3"

```

For Windows, create a powershell command (run_agent.ps1) and run:

```bash
command: ["powershell","-ExecutionPolicy", "Bypass", "-File", "${PROJECT_DIR}/run_agent.ps1","main.py"]
```

</details>

### 2. Dev Mode

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system and run below command in a separate terminal.

<details>

```bash
# Run the agent using `uv`:
uv run python main.py
```
</details>


## Example

<details>


```bash
# Input:
Please fetch the code of '2' PR in repo 'renxinxing123/camel-software-testing'.

# Output:
The PR was successfully checked out. Local repository path: /home/xinxing/coraliser-/coral_examples/github-repo-understanding+unit_test_advisor/camel-software-testing
```
</details>


## Creator Details
- **Name**: Xinxing
- **Affiliation**: Coral Protocol
- **Contact**: [Discord](https://discord.com/invite/Xjm892dtt3)