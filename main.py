import warnings
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()
warnings.filterwarnings("ignore")

auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
github_client = Github(auth=auth)
anthropic_client = Anthropic()

print("clients loaded!")

def get_pr_metadata(repo, pr_number):
    pr = github_client.get_repo(repo).get_pull(pr_number)
    return {
        "title": pr.title,
        "body": pr.body, 
        "author":pr.user.login,
        "isDraft": pr.draft, 
        "state": pr.state,
        "isMerged": pr.merged, 
        "Mergeable": pr.mergeable,
        "ChangedFiled": pr.changed_files, 
        "linedAdded": pr.additions,
        "deletions":pr.deletions
    }

tools = [
    {
        "name": "get_pr_metadata",
        "description": "Gets PR Metadata from a PR",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "The repo that this PR belongs to"
                },
                "pr_number": {
                    "type": "integer",
                    "description": "The PR Number that we want to retrieve metadata from"
                }
            },
            "required": ["repo", "pr_number"]
        }
    }, 
]

user_input = input("Give me a repo and PR that you want me to review!\n") 
messages = [{"role": "user", "content": user_input}]
    
# Step 1 — First call to Claude
response = anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

#Step 2: For each turn, loop if we need to use a tool 
# (That means we need to execute code in our project)
while response.stop_reason == "tool_use":

    # EACH TURN: 
    # For each block in a turn (every tool request within a turn)
    tool_results = []
    for block in response.content: 
        # Execute get_pr_metadata tool, if requested
        if block.type == "tool_use" and block.name == "get_pr_metadata":
            repo = block.input["repo"]
            pr_number = block.input["pr_number"]
            content = get_pr_metadata(repo, pr_number)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(content)
            })

    # Step 3: Append all tools' responses into the message we want to feed into Claude
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    # Step 4 — Second call to Claude with the tool results
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    print("Stop reason:", response.stop_reason)
    print(response.content[0].text)
