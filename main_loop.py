import logging
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

from scraper import do_scrape
import settings
import time
import sys
import traceback
import requests

if __name__ == "__main__":
    while True:
        print("{}: Starting scrape cycle".format(time.ctime()))
        try:
            do_scrape()
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(time.ctime()))
        time.sleep(settings.SLEEP_INTERVAL)
