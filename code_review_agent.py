import anthropic
import os
import time
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()

# Clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
github_client = Github(os.getenv("GITHUB_TOKEN"))

def get_pr_diff(repo_name, pr_number):
    """Fetch PR diff from GitHub with error handling"""
    try:
        repo = github_client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        code_to_review = ""
        for file in pr.get_files():
            if file.patch:  # some files may have no diff (binary files etc)
                code_to_review += f"\n\n### File: {file.filename}\n"
                code_to_review += file.patch
        
        return pr, code_to_review
    except GithubException as e:
        print(f"GitHub error: {e.status} - {e.data}")
        raise

def review_code(code_to_review, retries=3):
    """Send code to Claude with retry logic"""
    for attempt in range(retries):
        try:
            response = anthropic_client.messages.create(
                model="claude-opus-4-5",
                max_tokens=2048,
                system="You are a senior software engineer doing code review. Be specific, concise, and actionable. For each issue found, mention the filename and line.",
                messages=[
                    {"role": "user", "content": f"Review this pull request:\n{code_to_review}"}
                ]
            )
            return response.content[0].text
        except anthropic.AuthenticationError:
            print("❌ Invalid API key — check your .env file")
            raise  # don't retry, it'll never work
        except anthropic.APIError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def post_review(pr, review):
    """Post review comment to GitHub PR"""
    try:
        pr.create_issue_comment(review)
        print("✅ Review posted to GitHub PR!")
    except GithubException as e:
        print(f"Failed to post review: {e.status} - {e.data}")
        raise

def main():
    repo_name = "wnqnguo/code-review-agent"  # change back
    pr_number = 1

    try:
        print("Fetching PR diff...")
        pr, code_to_review = get_pr_diff(repo_name, pr_number)

        if not code_to_review:
            print("No reviewable code found in this PR.")
            return

        print("Sending to Claude for review...")
        review = review_code(code_to_review)
        print(review)

        print("Posting review to GitHub...")
        post_review(pr, review)

    except Exception as e:
        print(f"\n❌ Agent failed: {e}")



if __name__ == "__main__":
    main()