from suds.client import Client
import traceback
import unittest

class TestWSIBankService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = 'http://localhost:8000/?wsdl'
        # suds likes to keep WSDL cached, make sure its fresh
        cls.client = Client(url)
        cls.client.options.cache.clear()
        cls.client = Client(url)


    def expect_exception(self, *args, **kwargs):
        func = kwargs.get('func', self.client.service.transfer)
        exception = kwargs.get('exception', Exception)
        self.assertRaises(exception, func, *args)

    def test_too_few_arguments(self):
        self.expect_exception('aesop')

    def test_negative_amount(self):
        self.expect_exception('aesop', 'F1234', 'B5678', -100)

    def test_transfer_to_same_account(self):
        self.expect_exception('aesop', 'F1234', 'F1234', 100)

    def test_correct_call(self):
        result = self.client.service.transfer('aesop', 'F1234', 'B5678', 100)
        self.assertEquals(result, 'OK')

if __name__ == '__main__':
    unittest.main()