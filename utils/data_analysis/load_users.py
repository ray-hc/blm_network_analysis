#!/Users/raycrist/local/bin/python3.8

# data_vis_geo_users.py
import pyarrow.feather as feather
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sqlitedict import SqliteDict

from ..common import constants as c

def load_users_dfs():
    try:
        users_df = feather.read_feather(c.USERS_FTR)
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        users_df = generate_users_dfs()
        feather.write_feather(users_df, c.USERS_FTR)

    geo_users_df = users_df[users_df[c.HAS_TAG]] 
    return users_df, geo_users_df

def generate_users_dfs():
    with SqliteDict(c.USERS_SQL) as u_dict:

        # Load in users:
        dSeries = []
        runs = 0
        for i, u in u_dict.items():
            try:
                dSeries.append((
                  i, 
                  u.following, 
                  u.followers, 
                  u.tweet_count, 
                  u.private, 
                  u.created_at, 
                  len(u.geos), 
                  u.used_prior if (hasattr(u, "used_prior")) else False
                ))
                if runs % 100000 == 0:
                    print(f"{runs} users imported.")
                runs += 1
            except Exception as e:      
                print(f"{e} at {i}")       # Will fail when a u_dict item isn't a user.

        users_df = pd.DataFrame.from_dict(dSeries)
        users_df.columns =[c.U_ID, c.FLWNG, c.FLWRS, c.TW_COUNT, c.PRIV, c.BORN, c.LOCS, c.PRIOR_ADOPTER]

        # Sort out now private users.
        users_df = users_df[~users_df[c.PRIV]]

        # Track if geotagged.
        users_df[c.HAS_TAG] = users_df[c.LOCS].apply(lambda len_geo: len_geo > 0)

        # Get birthday -- ISO formats autodetected...
        users_df[c.BORN] = pd.to_datetime(users_df[c.BORN])

        # Sometimes SQLiteDict gets stuck.
        u_dict.close(force=True)

    return users_df

