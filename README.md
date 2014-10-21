webservice
==========

A student project. Very barebones web services, not meant for deployment.

Requires Python 2.7 and various Python modules, all available through pip. Recommended you use virtualenv as well. 

To install dependencies, start up your virtualenv (recommended) and then run
pip install -r requirements.txt

To run services, start each service you want to test in a separate screen:
python bank_service_wsi.py
and
python bank_service_rest.py

Then run 
python bank_client.py -h
