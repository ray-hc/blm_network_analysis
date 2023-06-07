# Makefile for data-collection
# Ray Crist, 2021

# Since I called these Python scripts so regularly, 
# I used make commands to speed up startup.

.PHONY: tweets users geos prior-adopters friends activity

############
define TWTS_PY
from utils.data_collection import download_tweets
download_tweets.run()
endef
export TWTS_PY

tweets:
	python3 -c "$$TWTS_PY"
###########


############
define USERS_PY
from utils.data_collection import download_users
download_users.run()
endef
export USERS_PY

users:
	python3 -c "$$USERS_PY"
############


############
define GEOS_PY
from utils.data_collection import download_geos
download_geos.run()
endef
export GEOS_PY

geos:
	python3 -c "$$GEOS_PY"
############


############
define PRIOR_BOOL_PY
from utils.data_collection import download_prior_bool
download_prior_bool.run()
endef
export PRIOR_BOOL_PY

prior-adopters:
	python3 -c "$$PRIOR_BOOL_PY"
############

############
define FRIENDS_PY
from utils.data_collection import download_friends
download_friends.run()
endef
export FRIENDS_PY

friends:
	python3 -c "$$FRIENDS_PY"
###########

############
define ACTIVITY_PY
from utils.data_collection import download_activity
download_activity.run()
endef
export ACTIVITY_PY

activity:
	python3 -c "$$ACTIVITY_PY"
###########