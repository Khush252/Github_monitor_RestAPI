import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

async def get_httpx_client():
    return httpx.AsyncClient(timeout=httpx.Timeout(30))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_default_branch(repo_owner, repo_name, access_token):
    repo_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    async with (await get_httpx_client()) as client:
        response = await client.get(repo_url, headers=headers)
        response.raise_for_status()
        repo_info = response.json()
        return repo_info['default_branch']

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commit_diff(commit_sha, repo_owner, repo_name, access_token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3.diff'
    }
    async with (await get_httpx_client()) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                print("Rate limit exceeded or access denied while fetching commit diff")
            else:
                print(f"Error fetching commit diff: {exc.response.status_code} - {exc.response.text}")
            raise
    return response.text

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commits_from_github(repo_owner, repo_name, access_token, start_date, end_date):
    since_str = start_date.isoformat() + 'Z'
    until_str = end_date.isoformat() + 'Z'
    
    default_branch = await fetch_default_branch(repo_owner, repo_name, access_token)
    commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        'since': since_str,
        'until': until_str,
        'sha': default_branch,
        'per_page': 100,
        'page': 1
    }

    all_commits = []

    async with (await get_httpx_client()) as client:
        while True:
            try:
                response = await client.get(commits_url, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    print(f"Error fetching commits: {exc.response.status_code} - {exc.response.text}")
                    return all_commits  # Return empty list if repository or commits not found
                elif exc.response.status_code == 403:
                    print("Access denied or rate limit exceeded while fetching commits")
                    return all_commits  # Return empty list if access is denied
                else:
                    print(f"Error fetching commits: {exc.response.status_code} - {exc.response.text}")
                raise
            commits = response.json()
            if not commits:
                break
            all_commits.extend(commits)
            params['page'] += 1

    return all_commits

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_closed_prs(repo_owner, repo_name, access_token, start_date, end_date):
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
    params = {
        'state': 'closed',  # Fetch only closed PRs
        'sort': 'updated',
        'direction': 'desc',
        'per_page': 100,
        'page': 1
    }
    all_prs = []

    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 403:
                    print("Access denied or rate limit exceeded while fetching closed PRs")
                    return all_prs  # Return empty list if access is denied
                else:
                    print(f"Error fetching closed PRs: {exc.response.status_code} - {exc.response.text}")
                raise
            prs = response.json()
            if not prs:
                break
            all_prs.extend(prs)
            params['page'] += 1

    # Filter PRs by merged date
    filtered_prs = [
        pr for pr in all_prs if pr['merged_at'] and start_date <= datetime.fromisoformat(pr['merged_at'].rstrip('Z')) <= end_date
    ]
    return filtered_prs

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commits_in_pr(repo_owner, repo_name, pr_number, access_token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {'per_page': 100, 'page': 1}
    commits = []

    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 403:
                    print(f"Access denied or rate limit exceeded while fetching commits for PR #{pr_number}")
                    return commits  # Return empty list if access is denied
                else:
                    print(f"Error fetching commits for PR #{pr_number}: {exc.response.status_code} - {exc.response.text}")
                raise
            pr_commits = response.json()
            if not pr_commits:
                break
            commits.extend(pr_commits)
            params['page'] += 1

    return commits
