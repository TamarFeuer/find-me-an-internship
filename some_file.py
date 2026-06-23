import os

import requests
from dotenv import load_dotenv

load_dotenv()

params = {
    'app_id': os.getenv('ADZUNA_APP_ID'),
    'app_key': os.getenv('ADZUNA_APP_KEY'),
    'what': 'software developer',
    'what_exclude': 'senior',
    'where': 'amsterdam',
    'category': 'it-jobs',
    'results_per_page': 50,
}


def fetch_jobs():
    response = requests.get(
        'https://api.adzuna.com/v1/api/jobs/nl/search/1',
        params=params,
    )
    response.raise_for_status()
    return response.json()


def main():
    data = fetch_jobs()

    total = data.get('count', 0)
    results = data.get('results', [])
    print(f"Adzuna returned {total} total matches; showing {len(results)} on this page.\n")

    for i, job in enumerate(results, start=1):
        title = job.get('title', '(no title)')
        company = job.get('company', {}).get('display_name', '(unknown company)')
        location = job.get('location', {}).get('display_name', '(unknown location)')
        print(f"{i:2}. {title}")
        print(f"    {company} — {location}")


if __name__ == '__main__':
    main()
