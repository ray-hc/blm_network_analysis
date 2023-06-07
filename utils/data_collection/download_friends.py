from sqlitedict import SqliteDict
import datetime
import traceback
import time

from ..common import twitter_helpers as tw
from ..common import constants as c

# -----------------------------------------------------------
# download_friends.py
#
# Save to a simple SQL table (which can be used like a dict)
# a user's list of "friends" on Twitter, for all users who 
# tweeted in the given list of tweets (`TWTS_CSV`)
#
# -----------------------------------------------------------

PRINT_X_USERS = 30

last_req_time = time.time()   # global variable to track last JSON request.
hit_first_author = False      # global variable to let us know when we've started.

TWTS_CSV = c.GEO_TWTS_CSV # modify as needed. In my case, I only downloaded rich data for geotagged users.

def log_run_start(count):
    """Log the start of run!"""
    print(
      f"{c.SEPERATOR}\n"
      f"RUN at {datetime.datetime.now()}\n"
      f"Prev. saved: {count} users\n"
    )


def log_run_end(count, lines):
    """Announce state of progress at end of run."""
    print(
      f"Ending run. Users saved = {count}.\n"
      f"{lines} processed.\n"
      f"{c.SEPERATOR}\n"
    )


def download_friends(author_id):
    """
    Given a user, call Twitter's API to get their list of friends.
    If a user has more than 5000, a 'cursor' will be returned for next pg of results.
      Load the next page if necessary.
    Returns list of followers. 
    """
    global last_req_time    # Will update the last_req_time at end.

    params = {"user_id": author_id, "stringify_ids": True, "cursor": "-1"}
    friends = []

    while params['cursor'] != "0":
        time.sleep(tw.calc_wait_time(c.FRIENDS_WAIT_PD, last_req_time)) 
        last_req_time = time.time()

        json_resp = tw.connect_to_endpoint(c.FRIENDS_ENDPOINT, params)
        params['cursor'] = json_resp['next_cursor_str']
        for fr_id in json_resp['ids']:
            friends.append(fr_id)
        
    return friends


def save_friends(author_id, friends):
    with SqliteDict(c.FRIENDS_SQL) as friends_dict:
        friends_dict[author_id] = friends
        friends_dict[c.LAST_LINE] = friends_dict[c.LAST_LINE] + 1
        friends_dict.commit()


def run():
  
    with open(TWTS_CSV) as tweets:

        with SqliteDict(c.FRIENDS_SQL) as friends_dict:
            log_run_start(len(friends_dict))
            friends_dict[c.LAST_LINE] = friends_dict.get(c.LAST_LINE, 0)
            friends_dict[c.LAST_LINE] = 0 # un-comment this line to reset
            friends_dict.commit()
            tw.advance_to_line(tweets, friends_dict[c.LAST_LINE])

        last_run_had_err = False
        runs = 0

        while not tw.stdin_has_line():        # while the user hasn't interrupted
            tw_row = tweets.readline()        # read another line, until EOF
            if not tw_row or len(tw_row) <= 1:
                print("END OF FILE! Done.")
                break
            tweet = tw_row.split(',', 4)      # tRow = "id,author_id,created_at,geo"
            author_id = tweet[1]

            try:
                with SqliteDict(c.FRIENDS_SQL) as friends_dict:
                    author_saved_before = (author_id in friends_dict)

                if not author_saved_before:
                    # Save progress
                    friends = download_friends(author_id)
                    save_friends(author_id, friends)
                    # Log progress
                    runs += 1
                    if runs % PRINT_X_USERS == 0:
                        print(f"Saved {runs} users this round.")
                
                last_run_had_err = False # Update errors.

            except tw.TwitterUnauthException as e:
                if not author_saved_before:
                    save_friends(author_id, [-1])
                print(f"{e}\n...Unauth at uId={author_id}. Skipping.")
                time.sleep(tw.calc_wait_time(c.FRIENDS_WAIT_PD, last_req_time)) 

            except tw.Twitter404Exception as e:
                if not author_saved_before:
                    save_friends(author_id, [-2])
                print(f"{e}\n...404 at uId={author_id}. Skipping.")
                time.sleep(tw.calc_wait_time(c.FRIENDS_WAIT_PD, last_req_time)) 

            except tw.TwitterAPIException as e:
                print(
                  f"Download error at user: {author_id}\n"
                  f"{c.SEPERATOR}\n\n"
                )
                if not last_run_had_err:
                    last_run_had_err = True
                    time.sleep(tw.calc_wait_time(c.FRIENDS_WAIT_PD, last_req_time))
                    print("Resuming.")
                else:
                    print(
                      f"2nd error. Aborting.\n"
                      f"{c.SEPERATOR}\n\n"
                      )
                    break

            except Exception as e:
                print(
                  f"Error at user: {author_id}\n"
                  f"at time {datetime.datetime.now()}"
                  f"{c.SEPERATOR}\n"
                  f"{e}\n"
                  f"{traceback.format_exc()}\n"
                  f"{c.SEPERATOR}\n"
                )
                if not last_run_had_err:
                    last_run_had_err = True
                    time.sleep(c.ERR_WAIT_PD)
                    print("Resuming.")
                else:
                    print(
                      f"2nd error. Aborting.\n"
                      f"{c.SEPERATOR}\n\n"
                      )
                    break                       

        with SqliteDict(c.FRIENDS_SQL) as friends_dict:
            print(f"{c.SEPERATOR}\n")
            log_run_end(len(friends_dict), friends_dict[c.LAST_LINE])
