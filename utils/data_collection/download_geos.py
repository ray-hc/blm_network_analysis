from sqlitedict import SqliteDict
import json
import time
import datetime
import traceback

from ..common.user import Place
from ..common import twitter_helpers as tw
from ..common import constants as c

# -----------------------------------------------------------
# download_geos.py
# Given a list of tweets, download all those users' tweets in a given period
# which have a geotag, and save each geo-obj to that user along w/ the list
# of tweets for that user in which it appeared.
#
# -----------------------------------------------------------

TWTS_CSV = c.GEO_TWTS_CSV # modify as needed. In my case, I only downloaded rich data for geotagged users.

def download_geos(users_ids):
    """
    Given a set of users, call Twitter's API to get their data, and populate their objects in user dict.
    """
    params = {
      'query': f"{c.GEOS_QUERY} (from:{' OR from:'.join(users_ids)})",
      'tweet.fields': 'author_id,geo',
      'expansions': 'geo.place_id',
      'place.fields': 'geo,country_code,place_type',
      'start_time': '2020-05-25T04:00:00Z',
      'end_time': '2020-06-06T03:00:00Z',
      'max_results': c.TWTS_MAX_RESULTS,
    }
    json_resp = None
    while True:

        try:
            time.sleep(c.TWTS_WAIT_PD)
            json_resp = tw.connect_to_endpoint(c.TWTS_ENDPOINT, params)

            if "errors" in json_resp:
                print(json_resp["errors"])

            if json_resp["meta"]["result_count"] == 0:
                print(f"Empty results! PARAMS: {params}")
                break

            # Store reference to each geo_obj included...
            geo_objs = dict()
            if "includes" in json_resp:
                for pl in json_resp["includes"]["places"]:
                      geo_objs[pl["id"]] = pl
            else:
                print("Non-empty with no includes:")
                print(json.dumps(json_resp, indent=4, sort_keys=True))
                return

            with SqliteDict(c.USERS_SQL) as users_dict:
                for tweet in json_resp["data"]:
                    # Get tweet data:
                    tweet_id = tweet["id"]
                    u_id = tweet["author_id"]

                    if not ("geo" in tweet):
                        print(f"geo not in TW:{tweet_id}")
                        continue

                    pl_id = tweet["geo"].get("place_id", -1)
                    geo_obj = geo_objs.get(pl_id)
                    user = users_dict.get(u_id)

                    if not user:
                        print(f"{u_id} not in users_dict!")
                    elif not geo_obj:
                        print(f"Place ID = {pl_id} for {tweet_id}; geo: {tweet['geo']}")
                    else:
                        if pl_id not in user.geos:
                            user.geos[pl_id] = Place(geo_obj)  # A dict avoids repeating Geo's accidentally!
                        user.geos[pl_id].tweets.add(tweet_id)                  
                        users_dict[u_id] = user               # Then save!

                users_dict.commit()
            
            if "next_token" not in json_resp["meta"]:     # Update next token to finish this download!
                break
            else:
                params["next_token"] = json_resp["meta"]["next_token"]
        except:
            print(f"params:\n{params}\n{json_resp}]\n")
            raise

def run():

    with open(TWTS_CSV) as geo_users:

        # Keep track of how many lines have been reviewed so far. 
        # Advance to that point so we don't duplicate.
        with SqliteDict(c.USERS_SQL) as users_dict:
            users_dict[c.DWNLD_GEOS_LINES] = users_dict.get(c.DWNLD_GEOS_LINES, 0)
            # users_dict[c.DWNLD_GEOS_LINES] = 0 # un-comment this line to reset line count
            users_dict.commit()
            tw.advance_to_line(geo_users, users_dict[c.DWNLD_GEOS_LINES])

        processed = 0
        reached_end = False
        while not tw.stdin_has_line() and not reached_end:
            try:
                user_queue = []
                for _ in range(c.GEOS_MAX_USERS_PER_QUERY):    # load as many users at a time as Twitter allows.

                    tw_row = geo_users.readline()
                    if not tw_row:
                        reached_end = True      # boolean, to allow finishing downloading the final round before breaking.
                        print("END OF FILE!")
                        break

                    author_id = tw_row.split(',', 4)[1]
                    user_queue.append(author_id)

                download_geos(user_queue)         # do the adding to user_dict.
                processed += len(user_queue)      # should increment processed AFTER loading.

                if processed % 500 < 100:
                    print(f"Processed {processed} runs")

            except Exception as e:
                print(
                  f"Error after {processed} successful users at time {datetime.datetime.now()}."
                  f"{e}\n"
                  f"{traceback.format_exc()}\n"
                  f"{c.SEPERATOR}\n"
                )
                break

        # Save our total progress, and alert user.
        with SqliteDict(c.USERS_SQL) as users_dict:
            users_dict[c.DWNLD_GEOS_LINES] = users_dict[c.DWNLD_GEOS_LINES] + processed
            users_dict.commit()
            print(f"Total users processed: {users_dict[c.DWNLD_GEOS_LINES]}")


    



        


    




