import sys, os, base64, datetime, hashlib, hmac, time
import argparse
import logging
from suds.client import Client
from suds.sax.element import Element
import goodreads_rest
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
access_key, secret_key, associate_tag = keys = [os.environ.get(variable) for variable in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_ASSOCIATE_TAG']]

if not all(keys):
    print 'Not all access keys available.'
    sys.exit()

def generate_timestamp(gmtime):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

def generate_signature(operation, timestamp, secret_key):
    string = operation + timestamp
    sha = hmac.new(secret_key, string, hashlib.sha256)
    return base64.encodestring(sha.digest()).strip()

def search_keywords(*keywords):
    if not keywords:
        return {}
    if hasattr(keywords[0], '__iter__'):
        keywords = keywords[0]

    timestamp = generate_timestamp( time.gmtime() )
    signature = generate_signature( 'ItemSearch', timestamp, secret_key )

    #ItemSearch(xs:string MarketplaceDomain, xs:string AWSAccessKeyId, xs:string AssociateTag, xs:string XMLEscaping, xs:string Validate, ItemSearchRequest Shared, ItemSearchRequest[] Request, )

    client = Client('http://webservices.amazon.com/AWSECommerceService/AWSECommerceService.wsdl')

    # Add request signature to header. Amazon doesn't specify this in the WSDL, so it's a little messy
    aws = ('aws', "http://security.amazonaws.com/doc/2007-01-01/")
    key = Element('AWSAccessKeyId', ns=aws).setText(access_key)
    time_stamp = Element('Timestamp', ns=aws).setText(timestamp)
    sign = Element('Signature', ns=aws).setText(signature)

    client.set_options(soapheaders=(key, time_stamp, sign)) 

    searchRequest = client.factory.create('ItemSearchRequest')
    searchRequest.SearchIndex = 'Books'
    searchRequest.Keywords = keywords
    searchRequest.ResponseGroup = ['ItemAttributes']

    response = client.service.ItemSearch(
        AWSAccessKeyId=access_key, 
        AssociateTag=associate_tag,
        Request=[searchRequest],
        Timestamp=timestamp
    )

    print response

    books = dict()
    for item in response.Items[0].Item:
        info = item.ItemAttributes
        has_isbn = hasattr(info, 'ISBN')
        books[info.ISBN if has_isbn else item.ASIN] = {
            'title': info.Title,
            'authors': info.Author,
            'price': info.ListPrice if hasattr(info, 'ListPrice') else None,
            'has_isbn': has_isbn
        }
    reviews = goodreads_rest.get_reviews(books.keys())
    print type(reviews)
    pprint(reviews)
    pprint(books)
    for review in reviews:
        isbn = review['isbn']
        if not isbn in books:
            isbn = review['isbn13']
        books[isbn].update({
            'ratings_count': review['ratings_count'],
            'rating': review['average_rating']
        })
    return books

if __name__ == '__main__':
    pprint(search_keywords('magic', 'school', 'wizard'))
