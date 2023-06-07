
import os
import csv
import time
import datetime
import traceback

from ..common import twitter_helpers as tw
from ..common import constants as c


# -----------------------------------------------------------
# download_tweets.py
#
# Uses Twitter Academic Research API to download tweets containing 
# BlackLivesMatter in month after George Floyd for thesis project.
# Assumes Python 3.6+. 
#
# -----------------------------------------------------------


PAGES_MAX = 100000          # Defines how many 'pages' of tweets are downloaded per run. Good for testing. 
UPDATE_EVERY_X_PAGES = 20   # Don't print an update to the console every page -- just after x pages.

query_params = {
  'query': '#blacklivesmatter -is:nullcast',
  'tweet.fields': 'author_id,created_at,geo',
  'start_time': '2020-05-25T04:00:00Z',
  'end_time': '2020-06-07T04:00:00Z',
  'max_results': c.TWTS_MAX_RESULTS,
  }


def save_meta(json_resp):
    """
    Function to take a JSON_Response and write the relevant metadata to a metadata CSV (for debugging).
    """
    with open(c.META_TWTS_CSV, mode='a', newline='') as meta_csv:
        writer = csv.writer(meta_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
          json_resp["meta"]["newest_id"], 
          json_resp["meta"]["oldest_id"], 
          json_resp["meta"].get("next_token")
        ])


def save_tweets(json_resp):
    """
    Function to take a JSON_Response and write the tweets to tweet data CSV.
    """
    with open(c.TWTS_CSV, mode='a', newline='') as meta_csv:
        writer = csv.writer(meta_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for tweet in json_resp["data"]:
            writer.writerow([
              tweet["id"],
              tweet["author_id"],
              tweet["created_at"],
              tweet.get("geo")
            ])


def save_progress(count, pages_done):
    """Write the last query's token and count to save-file."""
    with open(c.SAVED_NXT_TOKEN_TWTS_FILE, "w") as saved_data:
        print(
          f"{query_params.get('next_token', '')}\n"
          f"{count}",
        file=saved_data)


def log_run_start():
    """Log the start of run!"""
    print(
      f"{c.SEPERATOR*2}\n"
      f"RUN at {datetime.datetime.now()}\n"
      f"Searching: {query_params['start_time']} - {query_params['end_time']}\n"
      f"{c.SEPERATOR}\n"
      f"Starting at next_token='{query_params.get('next_token', '')}'"
    )


def log_run_end(count, pages_done):
    """Log the end of the run!"""
    print(
      f"Succesfully completed {pages_done} pages, total tweet count = {count}.\n"
      f"Saved token to: '{query_params.get('next_token', '')}'\n"
      "\n"
    )


def load_saved_data():
    """
    Load saved token in from the last_token.
    Load and return the saved count.

    In retrospect, would have found a less hack-ish way of saving this!
    """
    count = 0
    if os.path.exists(c.SAVED_NXT_TOKEN_TWTS_FILE):
        with open(c.SAVED_NXT_TOKEN_TWTS_FILE, "r") as f:
            next_token = f.readline().rstrip()
            if next_token:
                query_params["next_token"] = next_token
            saved_count = f.readline().rstrip()
            print(f"Total prev. saved: '{saved_count}'")
            if saved_count:
              count = int(saved_count)
            
    return count


def run():
    """
    As long as there are more tweets to get and no std input, 
    fetch more pages of results.

    Calls time.sleep between calls to avoid rate limiting.
    """
    os.makedirs(c.TWEET_DIR, exist_ok=True)
    pages_done = 0
    count = load_saved_data()
    log_run_start()

    lastRunHadAPIError = False
    
    while pages_done < PAGES_MAX and not tw.stdin_has_line():
        try:
            json_resp = tw.connect_to_endpoint(c.TWTS_ENDPOINT, query_params)
            save_meta(json_resp)
            save_tweets(json_resp)
            count += json_resp["meta"]["result_count"]
            pages_done += 1
            
            if (pages_done % UPDATE_EVERY_X_PAGES == 1):
              print(f"Done downloading page {pages_done}, {count} total tweets saved.")

            if "next_token" not in json_resp["meta"]:
                print("No more next_token(s).")
                break
            else:
                query_params["next_token"] = json_resp["meta"]["next_token"]
                save_progress(count, pages_done)
                time.sleep(c.TWTS_WAIT_PD)       
            
            lastRunHadAPIError = False

        except tw.TwitterAPIException as e:
            print(
                "API Error.\n"
                f"Completely saved tweets: {count}. Next_token: {query_params.get('next_token')}.\n" 
            )
            if lastRunHadAPIError:
              print(f"Two API errors in a row. Terminating. Next_token: {query_params.get('next_token')}.")
              break     # stop downloading!
            else:
              lastRunHadAPIError = True
              print(f"Waiting {c.ERR_WAIT_PD} seconds before re-attempt.")
              time.sleep(c.ERR_WAIT_PD)
              print("Continuing.")

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(
              "Aborting, attempting to save progress.\n"
              f"Completely saved tweets: {count}. Next_token: {query_params.get('next_token')}.\n" 
              "Check that the last 100 results match the saved next_token.\n"
            )
            break

    save_progress(count, pages_done)
    log_run_end(count, pages_done)

if __name__ == "__main__":
    main()
