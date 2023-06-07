# "Contagion and #BlackLivesMatter: A Network Analysis"

This is the Github repo where I provide the code I used for collecting data on and analyzing the network of Twitter users who tweeted #BlackLivesMatter in the week after George Floyd's death.

# File Structure

```
.                     - root contains Makefile, Jupyter notebooks
./gephi_data          - network visualization data, excluded due to PII
./sim_results         - saving trained params for contagion models
./utils
  /common             - helper functions and User, Place object definitions
  /data_analysis      - scripts for loading dataframes and datasets
  /data_collection    - scripts for retrieving data from Twitter
```

# Data Collection

Over several months Fall 2021 / Winter 2022, I downloaded the following data from Twitter:

* All publicly available tweets containing the hashtag #BlackLivesMatter or #BLM from May 25th @ 12am ET to June 2nd 8pm, 2020.
* For each public hashtag adopter, I collected:
  * Account age
  * number of followers and friends (users they follow)
* For each adopter with at least 1 geotagged #BLM tweet during study period, I collected:
  * All geotagged tweets sent by user during study period
  * List of friends and followers as of Winter 2022
  * Tweet rate per hour from May 2nd to June 2nd

I initially wrote this code to be somewhat extensible, such that it could be easily modfied to conduct data collection for a myriad of Twitter network research projects. Since then, Twitter has announced it is deprecating the Academic API, so future research in this vein may be stifled, but this code is provided for transparency nonetheless.

## Make Commands

```bash
make tweets 
make users 

# download metadata about users
make geos 
make prior-adopters 
make friends 
make activity
```

## Steps

1. **Download tweets using the command `make tweets` (calls `download_tweets.py`).**

  * Each `make` command imports and runs a python script in `utils/data_collection` -- by running these scripts from the root directory, we can ensure they can access all the `utils/common` resources.
  * Twitter breaks down large query results into a paginated list of results; this code repeatedly queries the results, stepping through each page, until data collection is complete. This code was designed to be run on a personal computer;  for big datasets, you may not be able to fetch all in one sitting. By typing **any key and then enter**, the program will save its progress safely and can be restarted to continue at the current "page" of tweets. 
  * If the program **CRASHES** during download, it will attempt to save your current data, but check the last page of tweets to be sure.

2. **Download user information about those tweeters using `make users` (calls `download_users.py`).**

  * download_users.py downloads 100 users at a time, so each 100 "runs" (API calls) = 100,000 user objects populated.
  * If you have a large number of users, I suggest feeding a pre-processed version of the tweets CSV with only unique users (i.e. if a user posts multiple times, only include one of their tweets).

3. **Download additional information using `make prior-adopters|geos|friends|activity`**

  * To retrieve just geotagged users, I used a grep command to filter for #BLM tweets which contain a geotag.
  * I only retrieved detailed information about users who had a geotagged #BLM tweet to save time. These scripts, however, could be run on the whole population with enough time. Additionally, since `make geos` fetches geotags for all of a user's tweets, not just their #BLM tweets, the pool of geotagged users can also be furthur expanded before conducting additional analysis. I ran out of time to do this for this project.

## Installation:

The download scripts assume Python 3.6+.

Run the following terminal commands:

```
pip3 install pynput
pip3 install requests
pip3 install requests-oauthlib
pip install sqlitedict
conda install -c conda-forge pygeos
```

Create a `.env` file of format in the data-collection directory to include your log-in information: `TWIT_BEARER_TOKEN="{Your Token here.}"`

## Implementation

`make tweets` saves the list of tweets to a CSV, and stores the pagination token (how far in results we've saved) to the `.env` file.

I originally downloaded information about users using `SqliteDict`, which stores a simple dictionary `userID->userObject` in an SQL table. The structure of the `User` and `Place` (Twitter-defined location) objects is defined in `utils/common/user.py`

## Attributions

The `twitter_api_connect.py` script's connect_to_endpoint() and bearer_oauth() functions were copied from [Twitter's example code](https://github.com/twitterdev/Twitter-API-v2-sample-code).

# Analyzing Data

To analyze my data, I used a series of 4 Jupyter notebooks. These notebooks rely on functions in the `utils/data_analysis/load_..py` files, which convert the data stored in my .csv and .sqlite files into panda dataframes.

I also used several external datasets:

* [Mapping Police Violence](https://mappingpoliceviolence.org/)
* [American Community Survey](https://www.census.gov/programs-surveys/acs/data.html)
* [Social Explorer's 2019 Census-defined County Subdivisions](https://geodata.socialexplorer.com/collection/d33c1634-fcde-41df-85ed-77884be417c5) *Excluded from this repo as it is proprietary data. You should be able to find equivalent data on Census website for free; this copy is just formatted to be easy to work with.*

Finally, I estimated the number of news articles referencing #BlackLivesMatter by day using [Nexis Uni](https://www.lexisnexis.com/en-us/professional/academic/nexis-uni.page)

The 4 Jupyter notebooks are intended to be run in order, as some of the dataframes used in later notebooks are generated mid-analysis. Additionally, I use multiple non-deterministic algorithms such as K-Means Clustering, and in these cases, the latest output of the notebooks may defer from the data cited in my research.

## Installation

Truthfully, I cannot recall which packages I had to install for this, given that the installation of conda downloads packages such as `sklearn` by default. I think you at least need to install pyarrow:

```
conda install -c conda-forge pyarrow
```

## Implementation

In the process of data analysis, I discovered that `SqliteDict` was too slow to easily handle the amount of data I was working with. I shifted towards using `pandas` for most all data analysis, saving offline copies of my dataframes using `pyarrow.feather` (`.ftr` is an efficient file format for storing dataframes).
