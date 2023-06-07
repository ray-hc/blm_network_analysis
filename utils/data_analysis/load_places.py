import pyarrow.feather as feather
import pandas as pd
from sqlitedict import SqliteDict

from ..common import constants as c

'''
Note: I use "places" to refer to geotags, 
and "locations" to refer to aggregate, calculated user locations.

A row is added for each user for each Twitter-defined geographic region/point.
(1 user may have multiple rows for different locations,
and 1 place may have been tagged by many users).
'''


def load_places_df():

    try:
        places_df = feather.read_feather(c.PLACES_FTR)
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        places_df = generate_places_df()
        feather.write_feather(places_df, c.PLACES_FTR)
    return places_df


def generate_places_df():

    df = None
    with SqliteDict(c.USERS_SQL) as u_dict:
      
        dSeries = []
        runs = 0
        
        for i, u in u_dict.items():
          try:
              if len(u.geos) > 0:
                  for pl_id, pl in u.geos.items():
                      dSeries.append((pl_id, pl.full_name, pl.place_type, pl.country_code, i, pl.tweets, pl.geo))
              if runs % 10000 == 0:
                print(f"{runs} users' information imported.")
              runs += 1
          except Exception as e:
              print(e)
              print(i, u)

        places_df = pd.DataFrame.from_dict(dSeries)
        places_df.columns =[c.PL_ID, c.PL_NAME, c.PL_TYPE, c.C_CODE, c.U_ID, c.NUM_TWEETS, c.GEOTAG]
        u_dict.close(force=True)

    return places_df
