import sys, os, base64, datetime, hashlib, hmac, time
import argparse
import logging
from suds.client import Client
from suds.sax.element import Element
import goodreads_rest
import requests
from key_conf import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG = keys = [os.environ.get(variable) for variable in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_ASSOCIATE_TAG']]

# if not all(keys):
#     print 'Not all access keys available.'
#     sys.exit()

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
    signature = generate_signature( 'ItemSearch', timestamp, AWS_SECRET_ACCESS_KEY )

    #ItemSearch(xs:string MarketplaceDomain, xs:string AWSAccessKeyId, xs:string AssociateTag, xs:string XMLEscaping, xs:string Validate, ItemSearchRequest Shared, ItemSearchRequest[] Request, )

    client = Client('http://webservices.amazon.com/AWSECommerceService/AWSECommerceService.wsdl')

    # Add request signature to header. Amazon doesn't specify this in the WSDL, so it's a little messy
    aws = ('aws', "http://security.amazonaws.com/doc/2007-01-01/")
    key = Element('AWSAccessKeyId', ns=aws).setText(AWS_ACCESS_KEY_ID)
    time_stamp = Element('Timestamp', ns=aws).setText(timestamp)
    sign = Element('Signature', ns=aws).setText(signature)

    client.set_options(soapheaders=(key, time_stamp, sign)) 

    searchRequest = client.factory.create('ItemSearchRequest')
    searchRequest.SearchIndex = 'Books'
    searchRequest.Keywords = keywords
    searchRequest.ResponseGroup = ['ItemAttributes']

    response = client.service.ItemSearch(
        AWSAccessKeyId=AWS_ACCESS_KEY_ID, 
        AssociateTag=AWS_ASSOCIATE_TAG,
        Request=[searchRequest],
        Timestamp=timestamp
    )

    print response

    if not response.Items[0].TotalResults:
        return {}

    books = dict()
    for item in response.Items[0].Item:
        info = item.ItemAttributes
        has_isbn = hasattr(info, 'ISBN')
        books[info.ISBN if has_isbn else item.ASIN] = {
            'title': info.Title,
            'authors': info.Author if hasattr(info, 'Author') else ['Unknown'],
            'price': info.ListPrice if hasattr(info, 'ListPrice') else None,
            'has_isbn': has_isbn
        }
    reviews = goodreads_rest.get_reviews(books.keys())
    print type(reviews)
    #pprint(reviews)
    #pprint(books)
    for review in reviews:
        isbn = review['isbn']
        if not isbn in books:
            isbn = review['isbn13']
        if not isbn in books:
            # Some kind of weird error, who knows with these people, skip
            continue
        books[isbn].update({
            'ratings_count': review['ratings_count'],
            'rating': review['average_rating']
        })
    return books

def make_wsi_bank_transfer(cents, card, target_iban, message=None):
    # urls = ['http://demo.seco.tkk.fi/ws/1/WebServices/bank?WSDL', 'http://demo.seco.tkk.fi/ws/3/WebServices/bank?WSDL', 'http://demo.seco.tkk.fi/ws/5/?wsdl', 'http://demo.seco.tkk.fi/ws/6/t755300bank/services/v1/transactions?wsdl', 'http://demo.seco.tkk.fi/ws/8/service/bankTransfer?WSDL']
    # for url in urls:
    #     try:
    #         Client(url)
    #     except:
    #         print "Didin't work"
    #         continue
    client = Client('http://demo.seco.tkk.fi/ws/6/t755300bank/services/v1/transactions?wsdl', location='http://demo.seco.tkk.fi/ws/6/t755300bank/services/v1/transactions')
    print client
    pprint(client.service.__dict__)
    transaction = client.factory.create('visaTransaction')
    transaction.amountInCents = cents
    transaction.targetIBAN = target_iban
    for key, value in card.items():
        setattr(transaction.card, key, value)
    print transaction
    response = client.service.makeVisaTransaction(transaction)
    print response

def make_rest_bank_transfer(username, fromaccount, toaccount, amount):
    url = 'http://localhost:5000/users/' + username + '/accounts/' + fromaccount + '/transfers/'
    response = requests.post(url, data={'toAccount': toaccount, 'amount': amount})
    print response

if __name__ == '__main__':
    # pprint(search_keywords('magic', 'school', 'wizard'))
    # make_wsi_bank_transfer(100, {'number': '4620111122223333', 'owner': 'Card McCardson', 'validYear': 2016, 'validMonth': 7, 'csv': '000'}, '9876543210')
    make_rest_bank_transfer('somedude', 'main', 'us', 100)
