import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

async def get_httpx_client():
    # print("30 seconds timeout, retrying")
    return httpx.AsyncClient(timeout=httpx.Timeout(30))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commit_diff(commit_sha, repo_owner, repo_name, access_token):
    url = f'https://github.com/{repo_owner}/{repo_name}/commit/{commit_sha}.diff'
    headers = {'Authorization': f'token {access_token}'}
    async with (await get_httpx_client()) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                print("Rate limit exceeded while fetching commit diff")
            else:
                print(f"Error fetching commit diff: {exc.response.status_code} - {exc.response.text}")
            raise
    return response.text

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commits_from_github(repo_owner, repo_name, access_token, start_date, end_date):
    since_str = start_date.isoformat() + 'Z'
    until_str = end_date.isoformat() + 'Z'
    
    commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    headers = {'Authorization': f'token {access_token}'}
    params = {
        'since': since_str,
        'until': until_str,
        'sha': 'main',
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
                if exc.response.status_code == 403:
                    print("Rate limit exceeded while fetching commits")
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
    headers = {'Authorization': f'token {access_token}'}
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
    params = {
        'state': 'closed',
        'sort': 'updated',
        'direction': 'desc',
        'per_page': 100,
        'page': 1,
        'since': start_date.isoformat() + 'Z',
        'until': end_date.isoformat() + 'Z'
    }
    all_prs = []

    async with (await get_httpx_client()) as client:
        while True:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 403:
                    print("Rate limit exceeded while fetching closed PRs")
                else:
                    print(f"Error fetching closed PRs: {exc.response.status_code} - {exc.response.text}")
                raise
            prs = response.json()
            if not prs:
                break
            all_prs.extend(prs)
            params['page'] += 1

    return all_prs

def filter_merged_prs(prs):
    merged_prs = []
    for pr in prs:
        if pr['merged_at']:
            merged_prs.append(pr)
    return merged_prs

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_commits_in_pr(repo_owner, repo_name, pr_number, access_token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits'
    headers = {'Authorization': f'token {access_token}'}
    params = {'per_page': 100, 'page': 1}
    commits = []

    async with (await get_httpx_client()) as client:
        while True:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 403:
                    print(f"Rate limit exceeded while fetching commits for PR #{pr_number}")
                else:
                    print(f"Error fetching commits for PR #{pr_number}: {exc.response.status_code} - {exc.response.text}")
                raise
            pr_commits = response.json()
            if not pr_commits:
                break
            commits.extend(pr_commits)
            params['page'] += 1

    return commits
