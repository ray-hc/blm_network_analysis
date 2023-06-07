
import os
import json
from dotenv import load_dotenv
import datetime
import traceback
import time
from sqlitedict import SqliteDict

from ..common import twitter_helpers as tw
from ..common import constants as c

# -----------------------------------------------------------
# download_activity.py
#
# Save to User object the list of tweets per hour for each user.
# Need to know for simulations how often users post on Twitter
# to calculate activity rate. 
#
# -----------------------------------------------------------

query_params = {
  'granularity': 'hour',
  'end_time': '2020-06-03T00:00:00Z',
}

def run():

    # Go through all users,
    # and create a dictionary of users whose activity rate must be downloaded 
    with SqliteDict(c.USERS_SQL) as users_dict:

        to_add = dict()
        j = 0
        for u_id, user in users_dict.items(): 
            # if the item is a User object, a geotagged user, and has not had activity rate downloaded yet, 
            # then add to queue.
            if (not isinstance(user, int)) and (len(user.geos) > 0) and (len(user.activity_rate) == 0):
                to_add[u_id] = user
            j += 1
            if (j % 1000000 == 0):
                print(f"Loaded {j} users, {datetime.datetime.now()}")

        print(f"Loaded in To Add: {len(to_add)}, {datetime.datetime.now()}")

        # For each user, conduct a query just for their tweets,
        # and save the list of tweet counts for time period (oldest to newest)
        i = 0
        for u_id, user in to_add.items():
            try:
                query_params["query"] = f"-is:nullcast from:{u_id}"
                json_response = tw.connect_to_endpoint(c.COUNT_ENDPOINT, query_params)
                if "data" in json_response:
                    user.activity_rate = [time_pd["tweet_count"] for time_pd in json_response["data"]]
                    users_dict[u_id] = user
                    i += 1
                    if (i % 1000 == 0):
                        print(f"Processed {i} users, {datetime.datetime.now()}")
                        users_dict.commit() 
                else:
                    print(f"No data for {u_id}, json: {json_response}")
                time.sleep(c.COUNT_WAIT_PD) 
            except Exception as e:
                print(
                  f"Error at time {datetime.datetime.now()}"
                  f"{c.SEPERATOR}\n"
                  f"{e}\n"
                  f"{traceback.format_exc()}\n"
                  f"{c.SEPERATOR}\n"
                )
                users_dict.commit()
                time.sleep(c.ERR_WAIT_PD)
                print("Committed!")

                
