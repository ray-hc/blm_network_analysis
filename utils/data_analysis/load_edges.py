from sqlitedict import SqliteDict
from pyarrow import feather
import pandas as pd

from ..common import constants as c
from .load_users import load_users_dfs

"""
Loads all the edges into a dataframe,
where an edge from user A to B means
that user B follows user A (thus,
information flows from A->B).

Assumes that the "FRIENDS SQL" table
has already been created.
"""

def load_edges_df():

    try:
        edges_df = feather.read_feather(c.EDGES_FTR)
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        edges_df = generate_edges_df()
        feather.write_feather(edges_df, c.EDGES_FTR)

    return edges_df


def load_geo_edges_df():

    try:
        geo_edges_df = feather.read_feather(c.GEO_EDGES_FTR)
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        edges_df = load_edges_df()
        geo_edges_df = generate_geo_edges_df(edges_df)
        feather.write_feather(geo_edges_df, c.GEO_EDGES_FTR)

    return geo_edges_df 


def generate_edges_df():
    '''
    All edges' targets are geotagged users.
    This df includes those edges whose targets
    may not be geotagged.
    '''

    data = []
    with SqliteDict(c.FRIENDS_SQL) as friends_dict:
        
        runs = 0

        for u_id, friends_ids in friends_dict.items():
            if isinstance(friends_ids, list):
                for friend_id in friends_ids:
                    data.append((u_id, friend_id))
                runs += 1
                
            if runs % 1000 == 0:
                print(f"{runs} users loaded.")
                    
        print(f"Data length = {len(data)}")
        friends_dict.close(force=True)
        
    edges_df = pd.DataFrame(data, columns=["Target", "Source"])
    edges_df["Type"] = "Directed"
    edges_df["Weight"] = 1

    # pyarrow can't deal with ints for these columns for some reason.
    edges_df['Source'] = edges_df['Source'].astype(str)
    edges_df['Target'] = edges_df['Target'].astype(str)
   
    return edges_df

def generate_geo_edges_df(edges_df):
    '''
    I downloaded only geotagged users' friend information, 
    therefore, all edges' targets are geotagged users.
    This function filters out edges where
    source users which are not geotagged.
    '''

    _, geo_users_df = load_users_dfs()
    u_ids = geo_users_df[c.U_ID]

    geo_edges_df = edges_df.merge(u_ids, how='left', left_on="Source", right_on=c.U_ID)
    print(geo_edges_df)

    geo_edges_df = geo_edges_df.loc[geo_edges_df[c.U_ID].notna()]
    print(geo_edges_df)
    
    geo_edges_df = geo_edges_df.drop(c.U_ID, axis=1)
    return geo_edges_df