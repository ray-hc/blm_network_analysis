
from sqlitedict import SqliteDict
import geopandas as gpd
import matplotlib.pyplot as plt
from pyarrow import feather

from ..common import geo_helpers as g
from ..common import constants as c
from .load_places import load_places_df


'''
Load locations dataframe,
where a user's location is defined
as a user's most frquently-tagged location
over the search period,
provided that that user's mean location is within
30km of that spot + all geotags were in USA.
'''


def conv_to_geometry(geos_col):
    '''
    Convert Twitter geotags series into a series that GeoPandas can read.
    '''

    out = []
    for geo in geos_col:
        if 'bbox' in geo:
            out.append(g.polygon_from_bbox(geo))
        else:
            out.append('')
    return out


def load_locations_gdf():
    '''
    Note: In order to add/subtract/compute locations, you need flat-USA projections -- epsg:2163.
    Most data / mapping occurs in Geodetic lat/long projections -- epsg:4326.
    We're storing in epsg=2163, but returning in epsg:4326 because that's what 
    other resources will likely need.
    '''

    try:
        locations_df = gpd.read_feather(c.LOCS_FTR)
        locations_gdf = gpd.GeoDataFrame(locations_df, geometry=locations_df[c.CENTROID], crs="epsg:2163")
    except Exception as e:
        print(f"Feather failed:\n{e}\n")
        locations_gdf = generate_locations_gdf()
        locations_gdf.to_feather(c.LOCS_FTR)

    locations_gdf = locations_gdf.set_crs(epsg=2163)
    locations_gdf = locations_gdf.to_crs(epsg=4326)
    return locations_gdf


def generate_locations_gdf():

    places_df = load_places_df()
    places_df = places_df.explode(c.NUM_TWEETS, ignore_index=False)     # Create seperate row for each tweet.
    
    # Convert into a geo-capable dataframe.
    gdf = gpd.GeoDataFrame(
      places_df, 
      geometry=conv_to_geometry(places_df[c.GEOTAG])
    )

    # Set up GDF geometry. 
    gdf = gdf.set_crs(epsg=4326)  # Convert lat/lng coords
    gdf = gdf.to_crs(epsg=2163)   # to flat USA coords
    gdf = gdf.rename(columns={'geometry': 'geom'}).set_geometry('geom')
    gdf[c.CENTROID] = gdf.centroid
    gdf = gdf.set_geometry(c.CENTROID)

    # Track which geotags came from outside United States:
    gdf[c.FOREIGN] = gdf[c.C_CODE].apply(lambda c_code: c_code != c.US_CC)

    print("Viewing how many unique users in GDF:")
    print(gdf.groupby(gdf[c.U_ID]).count().describe())
    print(c.SEPERATOR)

    # Filter out non-valuable geotags.
    gdf = gdf[gdf[c.PL_TYPE] != c.PL_ADMIN]
    gdf = gdf[gdf[c.PL_TYPE] != c.PL_COUNTRY]

    # Set up mean/mode DFs
    mode_gdf = gdf.groupby(gdf[c.U_ID]).agg({
      c.CENTROID: g.mode_gdf_centroid,
      c.FOREIGN: 'any',
      c.PL_ID: 'nunique',
      c.NUM_TWEETS: 'count',
      c.FOREIGN: 'any',
    })
    mean_gdf = gdf.groupby(gdf[c.U_ID]).agg({
      c.CENTROID: g.mean_gdf_centroid,
      c.FOREIGN: 'any',
    })

    # Filter out users with a tweet in a foreign location.
    mean_gdf = mean_gdf.loc[lambda x: x[c.FOREIGN] == False]
    mode_gdf = mode_gdf.loc[lambda x: x[c.FOREIGN] == False]
    
    # Re-set geometry after creating new GDFs...
    mean_gdf = mean_gdf.set_geometry(c.CENTROID)
    mode_gdf = mode_gdf.set_geometry(c.CENTROID)

    print("GDF MEAN:")
    print(mean_gdf)
    print("GDF MODE:")
    print(mode_gdf)
    print(c.SEPERATOR)

    # Calculate distance between mode and mean location centroid. Sift out any with >30km variation.
    mode_gdf[c.GEO_DEV] = mode_gdf.distance(mean_gdf, align=False)
    mode_gdf = mode_gdf.loc[lambda x: x[c.GEO_DEV] < c.DIST_THRESHOLD]

    mode_gdf.reset_index(inplace=True)
    mode_gdf = mode_gdf.drop(['foreign'], axis=1)

    return mode_gdf
