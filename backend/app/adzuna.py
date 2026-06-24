import os

import requests
from dotenv import load_dotenv

# Read the variables from the .env file into the environment so os.getenv() can find them.
load_dotenv()


def fetch_jobs(what="software developer", where="amsterdam", what_exclude=""):
	# Build the query: credentials come from .env, search terms from the caller.
	params = {
		'app_id': os.getenv('ADZUNA_APP_ID'),   # credentials, kept out of the code in .env
		'app_key': os.getenv('ADZUNA_APP_KEY'),
		'what': what,                            # job title to search for
		'where': where,                          # location
		'what_exclude': what_exclude,            # words to drop, e.g. "senior"
		'category': 'it-jobs',                   # only IT jobs
		'results_per_page': 50,                  # up to 50 results per page
	}
	# Ask Adzuna for jobs matching `params`. The trailing /1 is the page number.
	response = requests.get(
		'https://api.adzuna.com/v1/api/jobs/nl/search/1',
		params=params,
	)
	# If Adzuna returned an error (bad key, rate limit, etc.), stop here with a clear error.
	response.raise_for_status()
	# Hand back the parsed JSON (a dict) so callers can use it.
	return response.json()
