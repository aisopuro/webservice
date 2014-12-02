import requests
import os, sys
from key_conf import GR_DEVELOPER_KEY, GR_SECRET_KEY
from pprint import pprint

STATS_URL = "http://www.goodreads.com/book/review_counts.json"

def get_reviews(isbns):
    if type(isbns) is not list:
        isbns = [isbns]

    reply = requests.get(STATS_URL, params={'key': GR_DEVELOPER_KEY, 'format': 'json', 'isbns': ','.join(isbns)})
    pprint(reply.text)
    if reply.status_code != 200:
        return {}
    else:
        return reply.json()['books']
