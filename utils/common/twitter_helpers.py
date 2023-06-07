import json
import os
import requests
import datetime
import sys
import select
import time
from dotenv import load_dotenv
from . import constants as c

# by RAY CRIST, October 2021

load_dotenv(c.ENV_PATH)
BEARER_TOKEN = os.environ.get("TWIT_BEARER_TOKEN")

class TwitterAPIException(Exception):
    pass

class TwitterUnauthException(Exception):
    pass

class Twitter404Exception(Exception):
    pass

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    (Copied verbatim from Twitter example code)
    """

    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"
    return r

def print_exception_msg(resp, query_params):
    """
    Write to the log file an explanation
    of the error.

    PARAMETERS:
    resp -- the requests.Response object from failed call to Twitter API.
    next_token -- the token that was used in the query, to be printed in log.
    """

    # Variables used in Prints:
    remaining = resp.headers.get("x-rate-limit-remaining", "N/A")
    limit = resp.headers.get("x-rate-limit-limit", "N/A")
    reset_sec = resp.headers.get("x-rate-limit-reset", "N/A")
    resp_text = json.dumps(json.loads(resp.text), indent=4, sort_keys=True)

    # Message
    print(
      f"{c.SEPERATOR}\n"
      f"{resp.status_code} Error at {datetime.datetime.now()}\n"
      f"Rate: {remaining} / {limit}, reset in {reset_sec} secs\n"
      f"{resp_text}\n"
    )
        

def connect_to_endpoint(url, query_params):
    """
    (Copied from Twitter example code)
    Modification: added print(get_exception_msg(...)).

    PARAMETERS:
    URL -- to connect to.
    params -- query parameter object.
    """

    response = requests.request("GET", url, auth=bearer_oauth, params=query_params)
    if response.status_code == 401:
        raise TwitterUnauthException("Unauthorized. See log for details.")
    elif response.status_code == 404:
        raise TwitterUnauthException("404. See log for details.")
    elif response.status_code != 200:
        print_exception_msg(response, query_params)
        raise TwitterAPIException(response.status_code, "See log for details.")
    return response.json()


def stdin_has_line():
  """
  Checks stdin. If not empty, then digest everything there (not commands) and return True.
  """
  has_line = False
  while sys.stdin in select.select([sys.stdin],[],[],0.0)[0]:     # digest everything in stdin.
      sys.stdin.readline()
      has_line = True
  return has_line


def advance_to_line(rFile, next_line):
    start_time = time.time()
    curr_line = 0
    while curr_line < next_line:
      rFile.readline()
      curr_line += 1
    print(f"Reached line {next_line} after {time.time()-start_time} seconds")


def calc_wait_time(WAIT_PD, last_req_time):    
    return max(0, WAIT_PD - (time.time() - last_req_time))