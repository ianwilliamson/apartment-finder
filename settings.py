from shapely.geometry.polygon import Polygon
import os

## Price

# The minimum rent you want to pay per month.
MIN_PRICE = 1000

# The maximum rent you want to pay per month.
MAX_PRICE = 2800

MIN_FEET = 600

## Location preferences

# The Craigslist site you want to search on.
# For instance, https://sfbay.craigslist.org is SF and the Bay Area.
# You only need the beginning of the URL.
CRAIGSLIST_SITE = 'sfbay'

# What Craigslist subdirectories to search on.
# For instance, https://sfbay.craigslist.org/eby/ is the East Bay, and https://sfbay.craigslist.org/sfc/ is San Francisco.
# You only need the last three letters of the URLs.
AREAS = ["sby", "pen"]

# A list of neighborhoods and coordinates that you want to look for apartments in.  Any listing that has coordinates
# attached will be checked to see which area it is in.  If there's a match, it will be annotated with the area
# name.  If no match, the neighborhood field, which is a string, will be checked to see if it matches
# anything in NEIGHBORHOODS.
BOXES = {
}

# A list of neighborhood names to look for in the Craigslist neighborhood name field. If a listing doesn't fall into
# one of the boxes you defined, it will be checked to see if the neighborhood name it was listed under matches one
# of these.  This is less accurate than the boxes, because it relies on the owner to set the right neighborhood,
# but it also catches listings that don't have coordinates (many listings are missing this info).
NEIGHBORHOODS = []

## Transit preferences

# The farthest you want to live from a transit stop.
MAX_TRANSIT_DIST = 2 # miles

# Transit stations you want to check against.  Every coordinate here will be checked against each listing,
# and the closest station name will be added to the result and posted into Slack.
TRANSIT_STATIONS = {
    'lawrence':     [37.370444, -121.996069],
    'sunnyvale':    [37.378392, -122.030794],
    'mountainview': [37.394567, -122.075990],
    'sanantonio':   [37.407264, -122.107073]
}

POLYGONS = {
        'the_polygon': Polygon([
            (37.414816, -122.118444),
            (37.424473, -122.097250),
            (37.414551, -122.083682),
            (37.408535, -122.070044),
            (37.400691, -122.035674),
            (37.395649, -122.012829),
            (37.391176, -121.996054),
            (37.382011, -121.963947),
            (37.366082, -121.965050),
            (37.352382, -121.968590),
            (37.352181, -122.014118),
            (37.364261, -122.032507),
            (37.370669, -122.077826),
            (37.399521, -122.132630)
                        ])
}

## Search type preferences

# The Craigslist section underneath housing that you want to search in.
# For instance, https://sfbay.craigslist.org/search/apa find apartments for rent.
# https://sfbay.craigslist.org/search/sub finds sublets.
# You only need the last 3 letters of the URLs.
CRAIGSLIST_HOUSING_SECTION = 'apa'

## System settings

# How long we should sleep between scrapes of Craigslist.
# Too fast may get rate limited.
# Too slow may miss listings.
SLEEP_INTERVAL = 20 * 60 # 20 minutes

# Which slack channel to post the listings into.
SLACK_CHANNEL = "#housing"
SLACK_CHANNEL_IGNORED = "#housing-ignored"
# The token that allows us to connect to slack.
# Should be put in private.py, or set as an environment variable.
SLACK_TOKEN = os.getenv('SLACK_TOKEN', "")
SLACK_USERNAME = 'hal'
SLACK_AVATAR = ':red_circle:'

# Any private settings are imported here.
try:
    from private import *
except Exception:
    pass

# Any external private settings are imported from here.
try:
    from config.private import *
except Exception:
    pass
