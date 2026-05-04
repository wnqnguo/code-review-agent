# AI Code Review Agent

A GitHub pull request review agent powered by Claude AI. Point it at any PR and it automatically fetches the diff, analyzes the code, and posts a structured review as a comment.

## Demo

![Code Review Agent Demo](demo.png)

## How It Works

1. Fetches the PR diff from GitHub using the GitHub API
2. Sends the diff to Claude with a structured prompt
3. Posts the review back to the PR as a comment

## Architecture#
User provides PR number
↓
Fetch PR diff (GitHub API)
↓
Send to Claude (Anthropic API)
↓
Post review comment (GitHub API)

## Features

- Automatically fetches and reviews any GitHub PR
- Catches common issues: SQL injection, hardcoded secrets, resource leaks, division by zero
- Retry logic with exponential backoff for resilient API calls
- Skips binary files with no reviewable diff
- Unit tested with mocking — no real API calls needed to run tests
- Evals suite to measure review quality across known bad code patterns

## Setup

1. Clone the repo
2. Install dependencies:
   pip3 install anthropic PyGithub python-dotenv pytest

3. Create a `.env` file:
   ANTHROPIC_API_KEY=your-anthropic-key
   GITHUB_TOKEN=your-github-token

4. Run the agent:
   python3 code_review_agent.py

## Running Tests

python3 -m pytest test_agent.py -v

## Running Evals

python3 evals.py

## Tech Stack

- Python
- Anthropic Claude API (claude-opus-4-5)
- PyGithub
- pytest
