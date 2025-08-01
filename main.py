import os
import json
import logging
import subprocess
import traceback
import asyncio
import urllib.parse
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai_tools import MCPServerAdapter

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@tool("Checkout GitHub PR")
def checkout_github_pr(repo_full_name: str, pr_number: int) -> str:
    """
    Clone a GitHub repository and check out the branch associated with a specific pull request.

    Args:
        repo_full_name (str): GitHub repository in the format "owner/repo".
        pr_number (int): Pull request number.

    Returns:
        str: Absolute path to the local repository checked out to the PR branch.
    """
    print(f"Tool called: checkout_github_pr({repo_full_name}, {pr_number})")
    dest_dir = os.getcwd()
    print(f"Working directory: {dest_dir}")

    repo_name = repo_full_name.split('/')[-1]
    repo_url = f'https://github.com/{repo_full_name}.git'
    repo_path = os.path.join(dest_dir, repo_name)
    pr_branch = f'pr-{pr_number}'
    
    print(f"Repository URL: {repo_url}")
    print(f"Local path: {repo_path}")
    print(f"PR branch: {pr_branch}")

    try:
        if not os.path.exists(repo_path):
            print(f"Cloning repository {repo_url} to {repo_path}")
            subprocess.run(['git', 'clone', repo_url, repo_path], check=True)
            print("Clone completed successfully")
        else:
            print(f"Repository already exists at {repo_path}")

        try:
            print("Attempting to checkout main branch")
            subprocess.run(['git', '-C', repo_path, 'checkout', 'main'], check=True)
            print("Checked out main branch")
        except subprocess.CalledProcessError:
            try:
                print("Main branch not found, attempting to checkout master branch")
                subprocess.run(['git', '-C', repo_path, 'checkout', 'master'], check=True)
                print("Checked out master branch")
            except subprocess.CalledProcessError:
                print("Neither main nor master branch found, continuing with current branch")
                pass

        print("Checking existing branches")
        existing_branches = subprocess.run(['git', '-C', repo_path, 'branch'], capture_output=True, text=True).stdout
        print(f"Existing branches: {existing_branches}")
        
        if pr_branch in existing_branches:
            print(f"Deleting existing PR branch: {pr_branch}")
            subprocess.run(['git', '-C', repo_path, 'branch', '-D', pr_branch], check=True)

        print(f"Fetching PR #{pr_number}")
        subprocess.run(['git', '-C', repo_path, 'fetch', 'origin', f'pull/{pr_number}/head:{pr_branch}'], check=True)
        print(f"Checking out PR branch: {pr_branch}")
        subprocess.run(['git', '-C', repo_path, 'checkout', pr_branch], check=True)
        
        result_path = os.path.abspath(repo_path)
        print(f"Successfully checked out PR. Repository path: {result_path}")
        return result_path
    
    except subprocess.CalledProcessError as e:
        error_message = f"Git operation failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"
        print(f"ERROR: {error_message}")
        return f"Error: {error_message}"
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(f"ERROR: {error_message}")
        traceback.print_exc()
        return f"Error: {error_message}"
        
async def get_tools_description(tools):
    descriptions = []
    for tool in tools:
        tool_name = tool.name
        schema = tool.args_schema.schema() if hasattr(tool, 'args_schema') and tool.args_schema else {}
        arg_names = list(schema.get('properties', {}).keys()) if schema else []
        description = tool.description or 'No description available'
        schema_str = json.dumps(schema, default=str).replace('{', '{{').replace('}', '}}')
        descriptions.append(
            f"Tool: {tool_name}, Schema: {schema_str}"
        )
    return "\n".join(descriptions)

async def setup_components(MCP_SERVER_URL):
    # Load LLM
    llm = LLM(
        model=os.getenv("MODEL_NAME"),
        temperature=float(os.getenv("MODEL_TEMPERATURE")),
        max_tokens=int(os.getenv("MODEL_MAX_TOKENS")),
        api_key=os.getenv("MODEL_API_KEY"),
    )

    # MCP Server
    serverparams = {"url": MCP_SERVER_URL,"timeout": 300, "sse_read_timeout": 300}
    mcp_server_adapter = MCPServerAdapter(serverparams)
    mcp_tools = mcp_server_adapter.tools
    agent_tools = mcp_tools + [checkout_github_pr]

    # GitClone Agent
    gitclone_agent = Agent(
        role="Git Clone Agent",
        goal="Clone GitHub repositories and check out branches for specific Pull Requests. Continue running until a PR is successfully checked out.",
        backstory="I am responsible for cloning GitHub repositories and checking out branches associated with specific pull requests. I will not stop until I successfully check out a PR.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=agent_tools
    )

    return gitclone_agent, agent_tools

async def main():

    runtime = os.getenv("CORAL_ORCHESTRATION_RUNTIME", None)
    if runtime is None:
        load_dotenv()

    base_url = os.getenv("CORAL_SSE_URL")
    agentID = os.getenv("CORAL_AGENT_ID")

    coral_params = {
        "agentId": agentID,
        "agentDescription": "An agent that takes the user's input and interacts with other agents to fulfill the request"
    }

    query_string = urllib.parse.urlencode(coral_params)

    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    logger.info(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    print("Initializing GitClone system...")
    gitclone_agent, agent_tools = await setup_components(CORAL_SERVER_URL)
    tools_description = await get_tools_description(agent_tools)
    print(tools_description)

    task = Task(
        description="""You are `gitclone_agent`, responsible for cloning a GitHub repository and checking out the branch for a specific pull request.

        1. Use `wait_for_mentions(timeoutMs=60000)` to wait for instructions from other agents.
        2. When a mention is received, record the `threadId` and `senderId`.
        3. Check if the message asks to checkout a PR with a given repo name and PR number.
        4. Extract `repo` and `pr_number` from the message.
        5. Call `checkout_github_pr(repo_full_name=repo, pr_number=pr_number)` to clone and checkout the PR.
        6. If the call is successful, send a message using `send_message` to the sender, saying the PR was checked out with the local path.
        7. If the call fails, send the error message using `send_message` to the sender.
        8. If the message format is invalid or incomplete, skip it silently.
        9. Do not create threads; always use the `threadId` from the mention.
        10. Wait 2 seconds and repeat from step 1.
        These are the list of all tools: {tools_description}
        """,
        agent=gitclone_agent,
        expected_output="Successfully checked out PR branch and provided the local repository path",
        async_execution=True
    )

    crew = Crew(
        agents=[gitclone_agent],
        tasks=[task],
        verbose=True,
        enable_telemetry=False
    )


    while True:
        try:
            print("Kicking off crew execution")
            result = crew.kickoff()
            print(f"Crew execution completed with result: {result}")
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in GitClone main loop: {str(e)}", exc_info=True)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
    print("GitClone Agent script completed")