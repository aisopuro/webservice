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

class User(ComplexModel):
    _type_info = [
        ('username', String),
        ('firstname', String),
        ('lastname', String)
    ]

class DB(object):
    def __init__(self, entries):
        self.structure = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(dict)
                )
            )
        )
        for entry in entries:
            self.structure['users'][entry['username']]['accounts'][entry['account']] = True
            self.structure['accounts'][entry['account']]['amount'] = entry['amount']

db = DB([
        {
            'username': 'aesop',
            'account': 'F1234',
            'amount': 40000
        },
        {
            'username': 'service',
            'account': 'B5678',
            'amount': 10**6
        }
    ])

db = dict(db.structure)
pprint(db)
class BankService(ServiceBase):

    @srpc(String, UnsignedInteger, _returns=Iterable(String))
    def say_hello(name, times):
        for i in xrange(times):
            yield 'Hello, {}'.format(name)

    @srpc(User)
    def login(user):
        print user

    @srpc(String, String, String, UnsignedInteger, _returns=String)
    def transfer(username, fromAccount, toAccount, amount):
        """Transfer money from user username, from account number fromAccount.
        Amount is cents to transfer.
        """
        user = db['users'].get(username)
        if not user:
            raise ResourceNotFoundError(username, 'User %s not found')
        has_account = user['accounts'].get(fromAccount)
        if not has_account:
            raise ResourceNotFoundError(fromAccount, 'User {} has no such account: %s'.format(username))
        if fromAccount == toAccount:
            print fromAccount, toAccount
            raise InvalidRequestError('', 'Cannot transfer to same account%s')
        target_account = db['accounts'].get(toAccount)
        if not target_account:
            raise ResourceNotFoundError(toAccount, 'No such account: %s')
        from_account = db['accounts'].get(fromAccount)
        if from_account['amount'] < amount:
            raise InvalidRequestError('', 'Not enough money for transaction%s')
        from_account['amount'] -= amount
        target_account['amount'] += amount
        return 'OK'
        


app = Application([BankService], 'aisopuro.bank.http',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
    )

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