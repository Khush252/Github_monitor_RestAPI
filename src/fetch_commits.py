from utils.github_api import fetch_commits_from_github


# fetch all commits
def fetch_all_commits(repo_owner, repo_name, access_token, start_date, end_date):
    return fetch_commits_from_github(
        repo_owner, repo_name, access_token, start_date, end_date
    )
