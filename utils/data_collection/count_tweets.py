
import os
import json
from dotenv import load_dotenv
from ..common import twitter_helpers as tw
from ..common import constants as c

# RAY CRIST, October 2021
# Simple call to the counts/all Twitter endpoint.

def main():
    query_params = {
      'query': '#blacklivesmatter -is:nullcast',
      'granularity': 'day',
      'start_time': '2020-05-25T04:00:00Z',
      'end_time': '2020-06-30T04:00:00Z',
    }
    json_response = tw.connect_to_endpoint(c.COUNT_ENDPOINT, query_params);
    print(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
