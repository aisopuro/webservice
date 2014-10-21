import argparse
from suds.client import Client
import requests

parser = argparse.ArgumentParser(description="Send some service requests")
parser.add_argument('-u', '--url', default='http://localhost', help="Base url for requests, default http://localhost")
parser.add_argument('-p', default=8000, help="Port, default 8000")
parser.add_argument('-r', default=False, action='store_true', help="Use REST service instead of WS-I. Changes port to 5000 if port wasn't set explicitly with -p")

def call_wsi(username, fromAccount, toAccount, amount):
    client = Client(wsi_url)
    try:
        response = client.service.transfer(username, fromAccount, toAccount, amount)
    except Exception as e:
        print e
    else:
        print response

def call_rest(username, fromAccount, toAccount, amount):
    rest_url = base_url + '/users/{}/accounts/{}/transfers/'.format(username, fromAccount)
    data = {
        'toAccount': toAccount,
        'amount': amount
    }
    response = requests.post(rest_url, data)
    print response.text

args = parser.parse_args()
if not args.r:
    to_call = call_wsi
    port = args.p
else:
    to_call = call_rest
    port = 5000 if type(args.p) is not str else args.p
base_url = args.url + ':' + str(port)

wsi_url = base_url + '/?wsdl'

keepGoing = True
yes = set(['yes', 'y'])
no = set(['no', 'n'])
while keepGoing:
    username = raw_input('Transfer from user [someuser]:') or 'someuser'
    fromAccount = raw_input("Transfer from user's account [someaccount]:") or 'someaccount'
    toAccount = raw_input("Transfer to account [someotheraccount]:") or 'someotheraccount'
    amount = raw_input("Amount of money (in cents) [100]") or 100
    print ''
    print "Transferring {} euros from {}'s account {} to account {}".format(amount / 100, username, fromAccount, toAccount)
    print "Service says:"
    to_call(username, fromAccount, toAccount, amount)
    print ''
    cont = raw_input('Keep going? [Y/n]')
    keepGoing =  not cont or cont.lower() in yes
print "Quit"
