from sqlitedict import SqliteDict
import json
import time

from ..common.user import User
from ..common import twitter_helpers as tw
from ..common import constants as c

# download_prior_bool.py
# *--------------*
# Check whether a user tweeted #blacklivesmatter before the study period, updates their user object in user dict.
# Assumes that a user has already been added to users_dict.

query_params = {
  'start_time': '2006-03-21T00:00:00Z',
  'end_time': '2020-05-25T03:59:00Z',
  'max_results': 10,
  }
QUERY_BASE = "#blacklivesmatter -is:nullcast"

def get_user_tw_count(u_id):
  '''
  Search for a user's tweets in the period in question 
  (after waiting a sleep-period to avoid) rate-limiting.
  Return the number of results*.

  *Note: will just return number for that *page* of results,
  so can only be used to see *whether* there are results,
  not how many.
  '''

  time.sleep(c.TWTS_WAIT_PD)
  query_params["query"] = f"{QUERY_BASE} from:{u_id}"
  try:
      json_resp = tw.connect_to_endpoint(c.TWTS_ENDPOINT, query_params)
  except:
      time.sleep(c.ERR_WAIT_PD)
      json_resp = tw.connect_to_endpoint(c.TWTS_ENDPOINT, query_params)
  num_prior_tweets = json_resp["meta"]["result_count"]
  print(f"{u_id} has {num_prior_tweets} prior tweets.")
  return num_prior_tweets


def run():

    with SqliteDict(c.USERS_SQL) as users_dict:
        for u_id, user in users_dict.items():
            # if not already downloaded, and a geotagged user, then do the download
            if (not hasattr(user, "used_prior")) and (hasattr(user, "geos")) and (len(user.geos) > 0):    
                if get_user_tw_count(u_id) > 0:
                    user.used_prior = True
                else:
                    user.used_prior = False
                users_dict[u_id] = user

        print("Finished loading users' prior-adopter records. Now updating the SQL.")
        users_dict.commit()


    
