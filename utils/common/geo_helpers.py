from shapely.geometry import Polygon, Point
from . import constants as c
from statistics import mean
import numpy as np
from scipy import stats

def convert_to_gjson_proper(geo):
    '''
    Twitter geo-objects lack the geometry property 
    typically required for manipulating GeoJSONs.
    
    RETURNS: new GeoJSON w/ polygon based on bounding box.


    Bounding box of form: east1(long), north1(lat), east2(long), north2(lat)
    '''
    b = geo["bbox"]
    geo["geometry"] = {
      "type": "Polygon",
      "coordinates": [
        [
            [b[0], b[1]],
            [b[0], b[3]],
            [b[2], b[3]],
            [b[2], b[1]],
        ]
      ]
    }
    return geo

def polygon_from_bbox(geo):

  b = geo["bbox"]
  poly = Polygon([           
    [b[0], b[1]],
    [b[0], b[3]],
    [b[2], b[3]],
    [b[2], b[1]]
  ])
  return poly


def geo_center_of(geo):
    if "geometry" not in geo:
        geo = convert_to_gjson_proper(geo)
    poly = Polygon(geo["geometry"]["coordinates"][0])
    return [poly.centroid.x, poly.centroid.y]


def geo_contains_geo(geoA, geoB):
    '''
    Given 2 GeoJSON objects in proper format,
    compute which is a child of which. 

    RETURNS: tbd.
    '''
    poly_a = Polygon(geoA["geometry"]["coordinates"][0])
    poly_b = Polygon(geoB["geometry"]["coordinates"][0])

    if poly_a.contains(poly_b):
      return "A"
    elif poly_b.contains(poly_a):
      return "B"
    else:
      return "C"


def calc_point(user_obj):

    points = []

    for _, pl in user_obj.geos.items():
        if not pl.country_code == c.US_CC:
            print(f"{pl.country_code} not in USA!")
            return None

        if pl.place_type not in [c.PL_ADMIN, c.PL_COUNTRY]:
            point = geo_center_of(pl.geo)
            for _ in pl.tweets:
                points.append(point)

    if len(points) == 0:
        print(user_obj)
        return None
    else:
        # latitude/longitude pairs
        return (mean([pt[1] for pt in points]), mean([pt[0] for pt in points]))


def mean_gdf_centroid(user_centroids):

    return Point(np.mean([pt.x for pt in user_centroids]), np.mean([pt.y for pt in user_centroids]))

def mode_gdf_centroid(user_centroids):

  pt_strs = []
  for pt in user_centroids:
    pt_strs.append(f"{pt.x},{pt.y}")
  
  mode_pt = stats.mode(pt_strs).mode[0]
  mode_pt_list = mode_pt.split(",")

  point = (float(mode_pt_list[0]), float(mode_pt_list[1]))
  return Point(point)
