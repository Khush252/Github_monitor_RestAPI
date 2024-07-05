from utils.content_utils import count_tests_in_diff
from collections import defaultdict
from utils.github_api import fetch_commit_diff, fetch_commits_from_github, fetch_closed_prs, fetch_commits_in_pr
from datetime import datetime

async def analyze_commit(commit_sha, repo_owner, repo_name, access_token):
    diff_content = await fetch_commit_diff(commit_sha, repo_owner, repo_name, access_token)
    test_count_change = count_tests_in_diff(diff_content)
    return test_count_change

async def analyze_commits_and_prs(repo_owner, repo_name, access_token, start_date, end_date):
    all_commits = await fetch_commits_from_github(repo_owner, repo_name, access_token, start_date, end_date)
    user_test_count = defaultdict(int)
    user_pr_count = defaultdict(int)

    def get_author_identifier(commit):
        if commit['author'] is not None:
            return commit['author']['login']
        return commit['commit']['author']['name']

    for commit in all_commits:
        if len(commit['parents']) == 1:
            author = get_author_identifier(commit)
            if author:
                test_count_change = await analyze_commit(commit['sha'], repo_owner, repo_name, access_token)
                user_test_count[author] += test_count_change
            else:
                print(f"Commit {commit['sha']} does not have an associated author. Skipping this commit.")

    all_prs = await fetch_closed_prs(repo_owner, repo_name, access_token, start_date, end_date)
    
    for pr in all_prs:
        pr_number = pr['number']
        commits_in_pr = await fetch_commits_in_pr(repo_owner, repo_name, pr_number, access_token)
        unique_authors = set()

        for commit in commits_in_pr:
            author = get_author_identifier(commit)
            if author:
                unique_authors.add(author)
            else:
                print(f"Commit {commit['sha']} in PR #{pr_number} does not have an associated author. Skipping this commit.")

        for author in unique_authors:
            user_pr_count[author] += 1

    return user_test_count, user_pr_count
