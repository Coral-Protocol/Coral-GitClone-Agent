import asyncio
import os
import json
import logging
from typing import List
from github import Github
from github.ContentFile import ContentFile
from github.GithubException import GithubException
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from anyio import ClosedResourceError
import urllib.parse
import subprocess
import traceback


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

base_url = os.getenv("CORAL_SSE_URL")
agentID = os.getenv("CORAL_AGENT_ID")

params = {
    # "waitForAgents": 1,
    "agentId": agentID,
    "agentDescription": """Responsible for cloning GitHub repositories and checking out branches associated with specific pull requests."""
}
query_string = urllib.parse.urlencode(params)
MCP_SERVER_URL = f"{base_url}?{query_string}"

def get_tools_description(tools):
    return "\n".join(f"Tool: {t.name}, Schema: {json.dumps(t.args).replace('{', '{{').replace('}', '}}')}" for t in tools)
    
@tool
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

async def create_repo_agent(client, tools):
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are `gitclone_agent`, responsible for cloning a GitHub repository and checking out the branch for a specific pull request. Following these step and never finish the chain:

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
         
        **Important: NEVER EVER end up the chain**
        
        Tools: {get_tools_description(tools)}"""),
        ("placeholder", "{history}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    model = init_chat_model(
        model=os.getenv("MODEL_NAME"),
        model_provider=os.getenv("MODEL_PROVIDER"),
        api_key=os.getenv("API_KEY"),
        max_tokens=os.getenv("MODEL_TOKEN")
    )


    agent = create_tool_calling_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, max_iterations=None ,verbose=True)

async def main():
    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    logger.info(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": 600,
                "sse_read_timeout": 600,
            }
        }
    )
    logger.info("Coral Server Connection Established")

    tools = await client.get_tools()
    coral_tool_names = [
        "list_agents",
        "create_thread",
        "add_participant",
        "remove_participant",
        "close_thread",
        "send_message",
        "wait_for_mentions",
    ]
    tools = [tool for tool in tools if tool.name in coral_tool_names]
    tools += [checkout_github_pr]

    logger.info(f"Tools Description:\n{get_tools_description(tools)}")

    agent_executor = await create_repo_agent(client, tools)

    while True:
        try:
            logger.info("Starting new agent invocation")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            logger.info("Completed agent invocation, restarting loop")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in agent loop: {str(e)}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
