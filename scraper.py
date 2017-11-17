from craigslist import CraigslistHousing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse
from util import post_listing_to_slack, find_points_of_interest
from slackclient import SlackClient
import time
import settings
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

engine = create_engine('sqlite:///listings.db', echo=False)

Base = declarative_base()

class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    train_stop = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def scrape_area(area):
    """
    Scrapes craigslist for a certain geographic area, and finds the latest listings.
    :param area:
    :return: A list of results.
    """
    cl_h = CraigslistHousing(site=settings.CRAIGSLIST_SITE, area=area, category=settings.CRAIGSLIST_HOUSING_SECTION,
            filters={'max_price': settings.MAX_PRICE, "min_price": settings.MIN_PRICE, "posted_today": True, 'min_ft2': settings.MIN_FEET} )

    results = []
    results_ignored = []
    gen = cl_h.get_results(sort_by='newest', geotagged=True, limit=20,include_details=True)
    while True:
        try:
            result = next(gen)
        except StopIteration:
            break
        except Exception:
            continue
        listing = session.query(Listing).filter_by(cl_id=result["id"]).first()

        # Don't store the listing if it already exists.
        if listing is None:
            if result["where"] is None:
                # If there is no string identifying which neighborhood the result is from, skip it.
                continue

            lat = 0
            lon = 0
            if result["geotag"] is not None:
                # Assign the coordinates.
                lat = result["geotag"][0]
                lon = result["geotag"][1]

                # Annotate the result with information about the area it's in and points of interest near it.
                geo_data = find_points_of_interest(result["geotag"], result["where"])
                result.update(geo_data)
            else:
                result["areaname"] = ""
                result["stationname"] = ""
                result["near_train"] = False

            # Try parsing the price.
            price = 0
            try:
                price = float(result["price"].replace("$", ""))
            except Exception:
                pass

            cats = 2
            body = result["body"].lower()
            if ("cats not allowed" in body) or ("no pets" in body) or ("no pet" in body):
                cats = 0
            elif (" cats " in body) or ("purrr" in body):
                cats = 1
            result["cats"] = cats

            # Create the listing object.
            listing = Listing(
                link=result["url"],
                created=parse(result["datetime"]),
                lat=lat,
                lon=lon,
                name=result["name"],
                price=price,
                location=result["where"],
                cl_id=result["id"],
                area=result["area"],
                train_stop=result["stationname"]
            )

            # Save the listing so we don't grab it again.
            session.add(listing)
            session.commit()

            # Return the result if it's near a bart station, or if it is in an area we defined.
#            if result["cats"] and (result["near_train"] or len(result["areaname"]) > 0):
            if result["cats"] and result["near_train"] and len(result["areaname"]) > 0:
                results.append(result)
            else:
                results_ignored.append(result)

    return (results,results_ignored)

def do_scrape():
    """
    Runs the craigslist scraper, and posts data to slack.
    """

    # Create a slack client.
    sc = SlackClient(settings.SLACK_TOKEN)

    # Get all the results from craigslist.
    all_results = []
    ignored_results = []
    for area in settings.AREAS:
        (results,results_ignored) = scrape_area(area)
        all_results += results
        ignored_results += results_ignored

    print("{}: Got {} good results, ignoring {} results".format(time.ctime(), len(all_results), len(ignored_results)))

    # Post each result to slack.
    for result in all_results:
        post_listing_to_slack(sc, result, channel = settings.SLACK_CHANNEL)

    for result in ignored_results:
        post_listing_to_slack(sc, result, channel = settings.SLACK_CHANNEL_IGNORED)

