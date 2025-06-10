### Responsibility

Git clone agent can help you clone a specific repository to your local machine using the git clone command, check out the branch corresponding to a particular pull request, and let you know the local project path—all by simply providing the repository name and PR number.

### Details

* Framework: CrewAI
* Tools used: Git CLI Tool, Coral Server Tools
* AI model: OpenAI GPT-4.1
* Date added: 02/05/25
* Licence: MIT

## Clone & Install Dependencies

1. Run [Coral Server](https://github.com/Coral-Protocol/coral-server)
<details>


This agent runs on Coral Server, follow the instrcutions below to run the server. In a new terminal clone the repository:


```bash
git clone https://github.com/Coral-Protocol/coral-server.git
```

Navigate to the project directory:
```bash
cd coral-server
```
Run the server
```bash
./gradlew run
```
</details>

2. Run [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent)
<details>


If you are trying to run Open Deep Research agent and require an input, you can either create your agent which communicates on the coral server or run and register the Interface Agent on the Coral Server. In a new terminal clone the repository:


```bash
git clone https://github.com/Coral-Protocol/Coral-Interface-Agent.git
```
Navigate to the project directory:
```bash
cd Coral-Interface-Agent
```

Install `uv`:
```bash
pip install uv
```
Install dependencies from `pyproject.toml` using `uv`:
```bash
uv sync
```

Configure API Key
```bash
export OPENAI_API_KEY=
```

Run the agent using `uv`:
```bash
uv run python 0-langchain-interface.py
```

</details>

3. Agent Installation

<details>
   
Clone the repository:
```bash
git clone https://github.com/Coral-Protocol/Coral-GitClone-Agent.git
```

Navigate to the project directory:
```bash
cd Coral-GitClone-Agent
```

**To run crewai agent, please switch to this branch:**
```bash
git checkout coral-server-crewai
```
If your multi-agents system includes crewai agent, **ALL** agents should be run on this server!

Install `uv`:
```bash
pip install uv
```

Install dependencies from `pyproject.toml` using `uv`:
```bash
uv sync
```

Copy the client sse.py from utils to mcp package
```bash
cp -r utils/sse.py .venv/lib/python3.10/site-packages/mcp/client/sse.py
```

This command will read the `pyproject.toml` file and install all specified dependencies in a virtual environment managed by `uv`.

</details>


### Configure Environment Variables

Copy the example file and update it with your credentials:

```bash
cp .env.example .env
```

Required environment variables:

* `OPENAI_API_KEY`

* **OPENAI_API_KEY:**
  Sign up at [platform.openai.com](https://platform.openai.com/), go to “API Keys” under your account, and click “Create new secret key.”

## Run Agent
Run the agent using `uv`:
```bash
uv run 1-crewai-GitCloneAgent.py
```

### Example Input/output

```bash
#Send message to the interface agent:
Please fetch the code of '2' PR in repo 'renxinxing123/camel-software-testing'.
```

```bash
The PR was successfully checked out. Local repository path: /home/xinxing/coraliser-/coral_examples/github-repo-understanding+unit_test_advisor/camel-software-testing
```

### Creator details

* Name: Xinxing
* Affiliation: Coral Protocol
* Contact: [Discord](https://discord.com/invite/Xjm892dtt3)
