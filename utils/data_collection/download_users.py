from sqlitedict import SqliteDict
import datetime
import traceback
import time

from ..common import twitter_helpers as tw
from ..common import constants as c
from ..common.user import User

# -----------------------------------------------------------
# download_users.py
#
# Given a set of tweets downloaded via download_tweets.py, will create/populate
# an SQLiteDict dictionary of user IDs to user objects containing users
# from those tweets.
#
# Some of these user objects have additional data saved to them in other functions,
# i.e. download_activity.py, but this intializes the dictionary
#
# -----------------------------------------------------------


## Allow overwriting of default tweet CSV, user dict.
TWTS_CSV = c.TWTS_CSV
USERS_DICT = c.USERS_SQL

# per how many API calls should we log our progress?
PRINT_X_RUNS = 100 

# Properties to download from Twitter's Users lookup.
PUBLIC_METRICS = "public_metrics"
FOLLOWERS_COUNT = "followers_count"
FOLLOWING_COUNT = "following_count"
TWEET_COUNT = "tweet_count"
PRIVATE = "protected"
CREATED_AT = "created_at"
USER_FIELDS = f"{PUBLIC_METRICS},{PRIVATE},{CREATED_AT}"


def log_run_end(lines):
    """Announce state of progress at end of run."""
    print(
      f"Ending run. {lines} processed.\n"
      f"{c.SEPERATOR}\n"
    )


def download_users(users_ids):
    """
    Given a set of users, call Twitter's API to get their data, and populate objects.
    Returns user objects.
    """
    params = {"ids": ",".join(users_ids), "user.fields": USER_FIELDS}
    json_resp = tw.connect_to_endpoint(c.USERS_ENDPOINT, params)
    user_objs = []

    for raw_user in json_resp["data"]:
      user = User(raw_user["id"])
      user.following = raw_user[PUBLIC_METRICS][FOLLOWING_COUNT]
      user.followers = raw_user[PUBLIC_METRICS][FOLLOWERS_COUNT]
      user.created_at = raw_user[CREATED_AT]
      user.tweet_count = raw_user[PUBLIC_METRICS][TWEET_COUNT]
      user.private = raw_user[PRIVATE]
      user_objs.append(user)

    return(user_objs)


def run():
  """
  The driver code for doing the user download, 
  to be called by a script in the root-level of directory (or Makefile)
  """
    last_req_time = time.time()
    with open(TWTS_CSV) as tweets:

        with SqliteDict(USERS_DICT) as users_dict:
            users_dict[c.LAST_LINE] = users_dict.get(c.LAST_LINE, 0) # manually set to 0 if adding a new CSV to a dictionary of users.
            users_dict.commit()
            tw.advance_to_line(tweets, users_dict[c.LAST_LINE])
            print(f"Beginning download at line {users_dict[c.LAST_LINE]}.")

        users_to_download = set()
        last_run_had_err = False
        temp_lines = 0
        runs = 0
        
        while not tw.stdin_has_line():        # while the user hasn't interrupted
            
            # read another line, until EOF
            tw_row = tweets.readline()        
            if not tw_row or len(tw_row) <= 1:
                print("END OF FILE! Done.")
                break

            # if valid line, increment line pointer, and get author_id
            temp_lines += 1
            tweet = tw_row.split(',', 4)
            author_id = tweet[1]

            try:
                users_to_download.add(author_id)

                # Each request takes 100 user_ids. When reached, run request.
                if len(users_to_download) == 100:
                    with SqliteDict(USERS_DICT) as users_dict:
                      
                        # Get user objects, and save to SQLiteDict.
                        user_objs = download_users(users_to_download)
                        for user_obj in user_objs:
                          users_dict[user_obj.user_id] = user_obj

                        # Save lines progress
                        users_dict[c.LAST_LINE] = users_dict[c.LAST_LINE] + temp_lines
                        temp_lines = 0

                        # Save all new info to dictionary.
                        users_dict.commit()
                        
                        # Print to log.
                        if runs % PRINT_X_RUNS == 0:
                            print(f"{runs} runs complete this round.")
                        runs += 1
                        
                        # Reset for next round
                        users_to_download = set()   

                        # If the wait has been less than 1, wait!
                        time.sleep(tw.calc_wait_time(c.USERS_WAIT_PD, last_req_time))
                        last_req_time = time.time()

            except Exception as e:
                print(
                  f"{c.SEPERATOR}\n"
                  f"{e}\n"
                  f"{traceback.format_exc()}\n"
                  f"at time {datetime.datetime.now()}"
                  f"{c.SEPERATOR}\n"
                )
                break

        with SqliteDict(USERS_DICT) as users_dict:
            log_run_end(users_dict[c.LAST_LINE])
