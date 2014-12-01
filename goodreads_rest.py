import requests
import os, sys
from pprint import pprint

dev_key, secret_key = keys = [os.environ.get(variable) for variable in [
'GR_DEVELOPER_KEY', 'GR_SECRET_KEY'
]]


ID_URL = "http://www.goodreads.com/book/isbn_to_id"
REVIEW_URL = "http://www.goodreads.com/book/show.json"
ISBN_URL = "http://www.goodreads.com/book/isbn"
STATS_URL = "http://www.goodreads.com/book/review_counts.json"

def get_reviews(isbns):
    if type(isbns) is not list:
        isbns = [isbns]

    reply = requests.get(STATS_URL, params={'key': dev_key, 'format': 'json', 'isbns': ','.join(isbns)})
    pprint(reply.json())
    if reply.status_code != 200:
        return {}
    else:
        return reply.json()['books']
