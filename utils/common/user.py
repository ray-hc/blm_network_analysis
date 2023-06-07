class User:
    '''
    A single Twitter user. 

    This doesn't represent all of the information I collected about users,
    as I shifted to storing all my data in feather-ed Panda dataframes once I 
    realized SQL was too slow, but this was the baseline class that I stored
    data in.s
    '''
    def __init__(self, user_id, following = -1, followers = -1, tweet_count = -1, created_at="0", private=False):
        self.user_id = user_id
        
        self.geos = dict()
        self.tweet_times = []

        self.following = following
        self.followers = followers
        self.tweet_count = tweet_count
        self.private = private

        self.created_at = created_at
        self.activity_rate = []

    def __str__(self):
        out = (
          f"{self.user_id}: FLRWS:{self.followers} FLWNG:{self.following} TWTS:{self.tweet_count}"
          f" BORN:{self.created_at} PRIV:{self.private} TW_TIMES:{self.tweet_times} GEOS: [\n"
        )
        for geo in self.geos:
          out += f"_____{str(self.geos[geo])},\n"
        out += "]"
        return out


class Place:
    '''
    Each Place class represented a Twitter-defined place, 
    which could be a country, country, etc. ,
    where `geo` represented a bounding box or single point (usually box).
    '''
    def __init__(self, geo_obj):

        self.place_id = geo_obj["id"]
        self.full_name = geo_obj["full_name"]
        self.country_code = geo_obj["country_code"]
        self.geo = geo_obj["geo"]
        self.place_type = geo_obj["place_type"]

        self.tweets = set()

    def __str__(self):
        return (
          f"{self.place_id}: NAME:{self.full_name} CC:{self.country_code} TYPE:{self.place_type} TWTS:{len(self.tweets)}\n"
          f"GEO_OBJ:{self.geo}"
        )



      
