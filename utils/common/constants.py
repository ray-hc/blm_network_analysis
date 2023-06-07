from pathlib import Path

# Get file path
root_path = Path(__file__).absolute().parent.parent
print(f"Path to Utils: {root_path}")
ENV_PATH = f"{root_path}/common/.env"

######################

DATA_COLLECTION = f"{root_path}/data_collection"

TWEET_DIR = f"{DATA_COLLECTION}/tweet_data"
TWTS_CSV = f"{TWEET_DIR}/sorted_tweets_thru02.csv"
META_TWTS_CSV = f"{TWEET_DIR}/download_tweet_meta.csv"
GEO_TWTS_CSV = f"{TWEET_DIR}/unique_geos_thru02.csv"
SAVED_NXT_TOKEN_TWTS_FILE = f"{TWEET_DIR}/saved_next_token.txt" # used to track how far along in saving process.

USER_DIR = f"{DATA_COLLECTION}/user_data"
USERS_SQL = f"{USER_DIR}/users.sqlite"
USERS_EXTRA_SQL = f"{USER_DIR}/users_extra.sqlite"
FRIENDS_SQL = f"{USER_DIR}/friends.sqlite"

#####################

DATA_ANALYSIS = f"{root_path}/data_analysis"

TWEETS_FTR = f"{DATA_ANALYSIS}/feathers/tweets_df.ftr"
GEO_TWEETS_FTR = f"{DATA_ANALYSIS}/feathers/geo_tweets_df.ftr"
EDGES_FTR = f"{DATA_ANALYSIS}/feathers/edges_df.ftr"
GEO_EDGES_FTR = f"{DATA_ANALYSIS}/feathers/geo_edges_df.ftr"
USERS_FTR = f"{DATA_ANALYSIS}/feathers/users_df.ftr"
GEO_USERS_FTR = f"{DATA_ANALYSIS}/feathers/geo_users_df.ftr"
PLACES_FTR = f"{DATA_ANALYSIS}/feathers/places_df.ftr"
LOCS_FTR = f"{DATA_ANALYSIS}/feathers/locs.ftr"

#####################

# Pandas Column Names
U_ID = "U_ID"
FLWNG = "Following"
FLWRS = "Followers"
TW_COUNT = "Tweets"
PRIV = "Private"
LOCS = "Locations"
BORN = "Born"
HAS_TAG = "Has Geotags"
NUM_LOCS = "Num of Unique Locs"
PERCENT = "Ratio Geotagged"

TW_ID = "Tw_ID"
CREATED_AT = "Timestamp" # 2  # 2=ISO8601 date
GEOS = "Geos"

#####################

# Twitter Endpoints:
USERS_ENDPOINT = "https://api.twitter.com/2/users"  
COUNT_ENDPOINT = "https://api.twitter.com/2/tweets/counts/all"
TWTS_ENDPOINT = "https://api.twitter.com/2/tweets/search/all"
FRIENDS_ENDPOINT = "https://api.twitter.com/1.1/friends/ids.json"   # using v1.1 since it has a higher limit for IDs per call.

# Twitter API Rules:
# *---------------*
# Wait periods based on API limits for given endpoints. See Twtr docs for latest.
# Twtr rules are based on 15-minute windows; these time-delays are avg. seconds between request
# based on that window.
TWTS_WAIT_PD = 3.2          
FRIENDS_WAIT_PD = 60        
ERR_WAIT_PD = 60         
USERS_WAIT_PD = 3
COUNT_WAIT_PD = 3

TWTS_MAX_RESULTS = 100      # Number of tweets per Tweets search call.

LAST_LINE = "last_line"     # For logging in SQLiteDict how far we got.
MISSED_USERS_TWTS_CSV = "missed_users.csv"
MISSED_USERS_LAST_LINE = "MISSED_USERS_LINES_READ"

DWNLD_GEOS_LINES = "download_geos_lines_processed"

GEOS_MAX_USERS_PER_QUERY = 29
GEOS_QUERY = "has:geo -is:nullcast"

#####################

# For Aesthetics:
SEPERATOR = "***********"

# SQL PRAGMA Rules:
MMAP_LIMIT = 3221225472   # Limit for how mcuh SQLite can store in active memory: 3GB in bytes
SET_PRAGMA_MMAP_LIMIT = f"PRAGMA MMAP_SIZE={MMAP_LIMIT}"

#####################

# Place Pandas Column Names
PL_ID = "PL_ID"
PL_NAME = "Name"
PL_TYPE = "Type"
C_CODE = "Country"
U_ID = "U_ID"
NUM_TWEETS = "Twts"
GEOTAG = 'Geotag'
PRIOR_ADOPTER = "prior_adopter"

# Geotag Entities
PL_ADMIN = 'admin'
PL_CITY = 'city'
PL_POI = 'poi'
PL_NBRHD = 'neighborhood'
PL_COUNTRY = 'country'
US_CC = 'US'

# Filtering Information
GEO_DEV = 'mean-mode dev.'
CENTROID = 'centroid'
FOREIGN = 'foreign'
IN_US = 'In_US'

# 
DIST_THRESHOLD = 30000 # Threshold beyond which, we decide we cannot pinpoint a user to single zipcode.