import os

import requests
from dotenv import load_dotenv

# Read the variables from the .env file into the environment so os.getenv() can find them.
load_dotenv()

# Search settings sent to Adzuna. app_id/app_key authenticate us; the rest define the query.
params = {
    'app_id': os.getenv('ADZUNA_APP_ID'),       # credentials, kept out of the code in .env
    'app_key': os.getenv('ADZUNA_APP_KEY'),
    'what': 'software developer',               # job title to search for
    'what_exclude': 'senior',                   # drop listings mentioning "senior"
    'where': 'amsterdam',                       # location
    'category': 'it-jobs',                      # only IT jobs
    'results_per_page': 50,                     # up to 50 results per page
}


def fetch_jobs():
    # Ask Adzuna for jobs matching `params`. The trailing /1 is the page number.
    response = requests.get(
        'https://api.adzuna.com/v1/api/jobs/nl/search/1',
        params=params,
    )
    # If Adzuna returned an error (bad key, rate limit, etc.), stop here with a clear error.
    response.raise_for_status()
    # Hand back the parsed JSON (a dict) so callers can use it.
    return response.json()


def main():
    data = fetch_jobs()

    # `count` is the total number of matches Adzuna has; `results` is just this page of them.
    total = data.get('count', 0)
    results = data.get('results', [])
    print(f"Adzuna returned {total} total matches; showing {len(results)} on this page.\n")

    # Print each job. .get(..., default) avoids a crash if a field is missing.
    for i, job in enumerate(results, start=1):
        title = job.get('title', '(no title)')
        company = job.get('company', {}).get('display_name', '(unknown company)')
        location = job.get('location', {}).get('display_name', '(unknown location)')
        print(f"{i:2}. {title}")
        print(f"    {company} — {location}")


# Only run main() when this file is executed directly (not when imported by another file).
if __name__ == '__main__':
    main()
