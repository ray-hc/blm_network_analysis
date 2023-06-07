import matplotlib.pyplot as plt
import pandas as pd
from pyarrow import feather

from ..common import constants as c

# DATA_VIS_TWEETS.CSV
# For running statistics on the tweets and geotagged tweets CSV.
# ----------------------- #
#
# 

def load_tweets_dfs():

    try:
        tweets_df = feather.read_feather(c.TWEETS_FTR)
        geo_tweets_df = feather.read_feather(c.GEO_TWEETS_FTR)
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        geo_tweets_df, tweets_df = generate_tweets_dfs()
        feather.write_feather(tweets_df, c.TWEETS_FTR)
        feather.write_feather(geo_tweets_df, c.GEO_TWEETS_FTR)

    tweets_df[c.CREATED_AT] = tweets_df[c.CREATED_AT].dt.tz_convert("US/Eastern")
    geo_tweets_df[c.CREATED_AT] = geo_tweets_df[c.CREATED_AT].dt.tz_convert("US/Eastern")
    
    return tweets_df, geo_tweets_df


def generate_tweets_dfs():

    '''
    Return a tuple of form (df_geo, df_all) where the columns represent...
    TW_ID, AUTH_ID, CREATED_AT, GEOTAG

    ...of tweets in the CSV file.
    '''
        
    # Generate the GEO dataset...
    # geo_tweets_df = pd.read_csv(c.GEO_TWTS_CSV , header=None)
    # geo_tweets_df.columns =[c.TW_ID, c.U_ID, c.CREATED_AT, c.GEOS]
    #geo_tweets_df[c.CREATED_AT] = pd.to_datetime(geo_tweets_df[c.CREATED_AT])       # ISO formats autodetected...

    # Generate the ALL dataset...
    tweets_df = pd.read_csv(c.TWTS_CSV, header=None)
    tweets_df.columns =[c.TW_ID, c.U_ID, c.CREATED_AT, c.GEOS]
    tweets_df[c.CREATED_AT] = pd.to_datetime(tweets_df[c.CREATED_AT])       # ISO formats autodetected...

    geo_tweets_df = tweets_df[tweets_df[c.GEOS].notna()]

    return geo_tweets_df, tweets_df