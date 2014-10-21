from flask import Flask
from flask.ext.restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class BankSimple(Resource):
    def __init__(self):
        self.simpleparser = reqparse.RequestParser()
        self.simpleparser.add_argument('something', type=int)

    def post(self, user_id):
        args = self.simpleparser.parse_args()
        return "It's user {}! With something = {}".format(user_id, args['something'])

class BankRest(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('toAccount', required=True, type=str, help="(required) The account to which money should be transferred")
        self.parser.add_argument('amount', required=True, type=int, help="(required) The amount of money to be transferred in cents")

    def post(self, username, fromAccount):
        args = self.parser.parse_args()
        if args['amount'] <= 0:
            return "amount must be positive", 400
        if args['toAccount'] == fromAccount:
            return "Cannot transfer to same account", 400
        return "OK. Transferred {} euro from {}'s account {} to account {}".format(args['amount']/100, username, fromAccount, args['toAccount'])

api.add_resource(BankSimple, '/<string:user_id>')
api.add_resource(BankRest, '/users/<string:username>/accounts/<string:fromAccount>/transfers/')

if __name__ == '__main__':
    app.run(debug=True)