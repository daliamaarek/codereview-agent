# 🤖 Claude PR Review Agent

An agentic code review tool that uses Claude to automatically review GitHub Pull Requests. Point it at any PR, and it will fetch the metadata, analyse the diff, and post a structured review comment directly on the PR.

---

## What It Does

- Fetches PR metadata (title, description, author, merge status, lines changed)
- Retrieves the full file diff for every changed file
- Sends everything to Claude for analysis
- Posts a review comment back to the PR on GitHub — with an `APPROVE`, `REQUEST_CHANGES`, or `COMMENT` decision

---

## Setup

### Prerequisites

- Python 3.8+
- A GitHub account with a [Personal Access Token](https://github.com/settings/tokens) (needs `repo` scope)
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
git clone <your-repo-url>
cd <your-repo>
pip install anthropic PyGithub python-dotenv
```

### Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

> **Note:** `GITHUB_USERNAME` is used to prevent the agent from `APPROVE`-ing your own PRs — it will fall back to `COMMENT` instead.

---

## Usage

Run the script and follow the prompt:

```bash
python agent.py
```

You'll be asked to provide a repo and PR number:

```
Give me a repo and PR that you want me to review!
> owner/repo-name PR #42
```

The agent will fetch the PR, analyse it, and post the review directly to GitHub.

---

## How It Works

The agent uses Claude's **tool use** feature in an agentic loop:

```
User input
    │
    ▼
Claude decides which tools to call
    │
    ▼
Agent executes tools (GitHub API calls)
    │
    ▼
Results fed back to Claude
    │
    ▼
Loop repeats until Claude stops calling tools
    │
    ▼
Final review posted to GitHub PR
```

1. **First call** — Claude receives the user's input and decides to call `get_pr_metadata` and `get_pr_files` to understand the PR.
2. **Tool execution** — The agent runs those functions against the GitHub API and returns the results.
3. **Second call** — Claude analyses the metadata and diff, then calls `write_pr_comment` with its verdict.
4. **Review posted** — The agent submits the review to GitHub and exits.

---

## Tools

| Tool | Description |
|------|-------------|
| `get_pr_metadata` | Fetches PR title, description, author, draft status, merge state, and change counts |
| `get_pr_files` | Retrieves the list of changed files with their diffs (patches), additions, and deletions |
| `write_pr_comment` | Posts a review to the PR with one of three events: `APPROVE`, `REQUEST_CHANGES`, or `COMMENT` |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `anthropic` | Claude API client |
| `PyGithub` | GitHub API client |
| `python-dotenv` | Loads credentials from `.env` |
