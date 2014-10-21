from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase
from spyne.model.complex import Iterable
from spyne.model.primitive import UnsignedInteger
from spyne.model.primitive import String
from spyne.model.complex import ComplexModel
from spyne.server.wsgi import WsgiApplication
from collections import defaultdict
from spyne.error import ResourceNotFoundError, InvalidRequestError
from pprint import pprint

class BankService(ServiceBase):

    @srpc(String, String, String, UnsignedInteger, _returns=String)
    def transfer(username, fromAccount, toAccount, amount):
        """Transfer money from user username, from account number fromAccount.
        Amount is cents to transfer.
        """
        if fromAccount == toAccount:
            print fromAccount, toAccount
            raise InvalidRequestError('', 'Cannot transfer to same account%s')
        return 'OK'
        


app = Application([BankService], 'aisopuro.bank.http', in_protocol=Soap11(validator='lxml'), out_protocol=Soap11(),)

wsgi_application = WsgiApplication(app)

if __name__=='__main__':
    import logging
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()