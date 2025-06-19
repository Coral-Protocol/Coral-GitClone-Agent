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

## Use the Agent  

### 1. Clone & Install Dependencies


<details>  

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system and the [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent) is running on the Coral Server.  

```bash
# Clone the GitClone Agent repository
git clone https://github.com/Coral-Protocol/Coral-GitClone-Agent.git

# Navigate to the project directory
cd Coral-GitClone-Agent

# To run crewai agent, please switch to this branch:
git checkout coral-server-crewai
# If your multi-agents system includes crewai agent, ALL agents should be run on this server!

# Install `uv`:
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```
This command will read the `pyproject.toml` file and install all specified dependencies in a virtual environment managed by `uv`.

</details>

### 2. Configure Environment Variables
<details>

Get the API Key:
[OpenAI](https://platform.openai.com/api-keys)


```bash
cp -r .env.example .env
```

Add your API keys and any other required environment variables to the .env file.

</details>

### 3. Run Agent
<details>

Run the agent using `uv`:
```bash
uv run 1-crewai-GitCloneAgent.py
```
</details>

### 4. Example
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
