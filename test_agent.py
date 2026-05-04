import pytest
from unittest.mock import MagicMock, patch
from github import GithubException
import anthropic
from code_review_agent import get_pr_diff, review_code, post_review

# ---- get_pr_diff tests ----

def test_get_pr_diff_success():
    """Happy path — returns PR and diff"""
    mock_file = MagicMock()
    mock_file.filename = "bad_code.py"
    mock_file.patch = "+ def get_user(id): return db.query('SELECT * FROM users WHERE id=' + id)"

    mock_pr = MagicMock()
    mock_pr.get_files.return_value = [mock_file]

    mock_repo = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    with patch('code_review_agent.github_client') as mock_github:
        mock_github.get_repo.return_value = mock_repo
        pr, diff = get_pr_diff("wnqnguo/code-review-agent", 1)

    assert "bad_code.py" in diff
    assert "get_user" in diff

def test_get_pr_diff_repo_not_found():
    """GitHub 404 is raised cleanly"""
    with patch('code_review_agent.github_client') as mock_github:
        mock_github.get_repo.side_effect = GithubException(404, "Not Found")
        with pytest.raises(GithubException):
            get_pr_diff("wnqnguo/fake-repo", 1)

def test_get_pr_diff_skips_binary_files():
    """Files with no patch are skipped"""
    mock_file = MagicMock()
    mock_file.filename = "image.png"
    mock_file.patch = None

    mock_pr = MagicMock()
    mock_pr.get_files.return_value = [mock_file]

    mock_repo = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    with patch('code_review_agent.github_client') as mock_github:
        mock_github.get_repo.return_value = mock_repo
        pr, diff = get_pr_diff("wnqnguo/code-review-agent", 1)

    assert diff == ""

# ---- review_code tests ----

def test_review_code_success():
    """Returns review text on success"""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="SQL injection found on line 5")]

    with patch('code_review_agent.anthropic_client') as mock_anthropic:
        mock_anthropic.messages.create.return_value = mock_response
        review = review_code("some code")

    assert "SQL injection" in review

def test_review_code_auth_error_no_retry():
    """Auth errors are not retried"""
    with patch('code_review_agent.anthropic_client') as mock_anthropic:
        mock_anthropic.messages.create.side_effect = anthropic.AuthenticationError(
            message="invalid key", response=MagicMock(), body={}
        )
        with pytest.raises(anthropic.AuthenticationError):
            review_code("some code")

        # should only be called once, no retries
        assert mock_anthropic.messages.create.call_count == 1

# ---- post_review tests ----

def test_post_review_success():
    """Posts comment to PR"""
    mock_pr = MagicMock()
    post_review(mock_pr, "Great review!")
    mock_pr.create_issue_comment.assert_called_once_with("Great review!")

def test_post_review_github_error():
    """GitHub error on post is raised"""
    mock_pr = MagicMock()
    mock_pr.create_issue_comment.side_effect = GithubException(403, "Forbidden")
    with pytest.raises(GithubException):
        post_review(mock_pr, "Great review!")