import settings
import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def coord_distance(lat1, lon1, lat2, lon2):
    """
    Finds the distance between two pairs of latitude and longitude.
    :param lat1: Point 1 latitude.
    :param lon1: Point 1 longitude.
    :param lat2: Point two latitude.
    :param lon2: Point two longitude.
    :return: Miles distance.
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    miles = 0.621371 * 6367 * c
    return miles

def in_box(coords, box):
    """
    Find if a coordinate tuple is inside a bounding box.
    :param coords: Tuple containing latitude and longitude.
    :param box: Two tuples, where first is the bottom left, and the second is the top right of the box.
    :return: Boolean indicating if the coordinates are in the box.
    """
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False

def post_listing_to_slack(sc, listing, channel):
    """
    Posts the listing to slack.
    :param sc: A slack client.
    :param listing: A record of the listing.
    """
    cats=dict()
    cats[0] = ":cat::x:"
    cats[1] = ":cat::smiley_cat:"
    cats[2] = ""
    listing["cats"] = cats[listing["cats"]]

    if listing["area"] is None:
        listing["area"] = "____ sq ft"
    else:
        listing["area"] = listing["area"].replace("ft2"," sq ft")

    if listing["geotag"] is None:
        listing["geotag"] = [0,0]
    if 'train_dist' not in listing:
        listing["train_dist"] = 100 
    if 'stationname' not in listing:
        listing["stationname"] = '???????'

    desc = "*{}*, {} | {:.2f} mi - *{}* | <https://www.google.com/maps/?q={},{}|map> | {} <{}|{}>".format(
            listing["price"],
            listing["area"],
            listing["train_dist"],
            listing["stationname"],
            listing["geotag"][0],
            listing["geotag"][1],
            listing["cats"],
            listing["url"],
            listing["name"] )

    sc.api_call(
        "chat.postMessage", channel=channel, text=desc,
        username=settings.SLACK_USERNAME, icon_emoji=settings.SLACK_AVATAR
    )

def find_points_of_interest(geotag, location):
    """
    Find points of interest, like transit, near a result.
    :param geotag: The geotag field of a Craigslist result.
    :param location: The where field of a Craigslist result.  Is a string containing a description of where
    the listing was posted.
    :return: A dictionary containing annotations.
    """
    area_found = False
    areaname = ""
    min_dist = 1000
    near_train = False
    train_dist = 1000
    stationname = ""
    # Look to see if the listing is in any of the neighborhood boxes we defined.
    for a, polygon in settings.POLYGONS.items():
        if polygon.contains(Point(geotag)):
            areaname = a
            area_found = True

    # Check to see if the listing is near any transit stations.
    for station, coords in settings.TRANSIT_STATIONS.items():
        dist = coord_distance(coords[0], coords[1], geotag[0], geotag[1])
        if dist < min_dist:
            train_dist = dist
            min_dist = train_dist
            stationname = station
        if dist < settings.MAX_TRANSIT_DIST:
            near_train = True

    # If the listing isn't in any of the boxes we defined, check to see if the string description of the neighborhood
    # matches anything in our list of neighborhoods.
    if len(areaname) == 0:
        for hood in settings.NEIGHBORHOODS:
            if hood in location.lower():
                areaname = hood

    return {
        "area_found": area_found,
        "areaname": areaname,
        "near_train": near_train,
        "train_dist": train_dist,
        "stationname": stationname
    }
