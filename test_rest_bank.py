import requests
import unittest

class TestRestBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = 'http://localhost:5000/users/someuser/accounts/someaccount/transfers/'

    def test_correct_post_w_data(self):
        reply = requests.post(self.url, data={'toAccount':'someotheraccount', 'amount':50000})
        self.assertEquals(reply.status_code, 200)

    def test_correct_post_w_querystring(self):
        reply = requests.post(self.url + '?toAccount=someotheraccount&amount=50000')
        self.assertEquals(reply.status_code, 200)

    def test_transfer_same_account(self):
        reply = requests.post(self.url, data={'toAccount':'someaccount', 'amount':50000})
        self.assertEquals(reply.status_code, 400)

    def test_transfer_negative(self):
        reply = requests.post(self.url, data={'toAccount':'someaccount', 'amount':-1000})
        self.assertEquals(reply.status_code, 400)

    def test_missing_argument(self):
        reply = requests.post(self.url, data={'amount':1000})
        self.assertEquals(reply.status_code, 400)

if __name__ == '__main__':
    unittest.main()