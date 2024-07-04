import os
import pandas as pd
from datetime import datetime
from src.analyze_commits import analyze_commits_and_prs

async def generate_report(repo_owner, repo_name, access_token, start_date, end_date):
    user_test_count, user_pr_count = await analyze_commits_and_prs(repo_owner, repo_name, access_token, start_date, end_date)

    data = []
    users = set(user_test_count.keys()).union(set(user_pr_count.keys()))
    for user in users:
        tests_added = user_test_count.get(user, 0)
        prs_merged = user_pr_count.get(user, 0)
        data.append([user, tests_added, prs_merged])

    report = pd.DataFrame(data, columns=["User", "Tests Added", "PRs contributed"])
    print(report)

    if not os.path.exists('Reports'):
        os.makedirs('Reports')

    date_format = "%d-%m-%Y"
    start_date_str = start_date.strftime(date_format)
    end_date_str = end_date.strftime(date_format)

    file_name = f"Report({start_date_str} - {end_date_str}).csv"
    file_path = os.path.join('Reports', file_name)

    report.to_csv(file_path, index=False)
    
    return file_path, report
