# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest

from flask import Flask, g
from flaskext.payments import Payments, Transaction, Authorisation, PaymentTransactionValidationError

class TestCase(unittest.TestCase):

    TESTING = True

    # Based Gateway and Plugin from Martin Fowler PoAEE, which class to bind to
    # use for payments specified in configuration, and bound by the factory
    # Payments at startup.
    PAYMENT_API = 'PayPal'
    
    # Define PayPal Specific Stuff

    PAYPAL_API_ENDPOINT = 'https://api-3t.sandbox.paypal.com/nvp'
    PAYPAL_API_URL = 'https://www.sandbox.paypal.com/webscr&cmd=_express-checkout&token='
   
    def setUp(self):

        self.app = Flask(__name__)
        self.app.config.from_object(self)

        # need to keep personal API details out of scm
        self.app.config.from_pyfile('yourpaypal.settings')
        
        self.payments = Payments(self.app)

        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):

        self.ctx.pop()


def getValidExpressTransaction():
    trans = Transaction()
    trans.type = 'Express'
    trans.amount = 100
    trans.currency = "how?"
    return trans

def getValidTransaction():
    vals = {
        'amt': '9.95',
        'inv': 'inv',
        'custom': 'custom',
        'next': 'http://www.example.com/next/',
        'returnurl': 'http://www.example.com/pay/',
        'cancelurl': 'http://www.example.com/cancel/',
        'firstname': 'Brave',
        'lastname': 'Star',
        'street': '1 Main St',
        'city': u'San Jose',
        'state': 'CA',
        'countrycode': 'US',
        'zip': '95131',
        'expdate': '012019',
        'cvv2': '037',
        'acct': '4797503429879309',
        'creditcardtype': 'visa',
        'ipaddress': '10.0.1.199',
        }

class TestTransaction(TestCase):

    def test_initialize(self):
        trans = getValidTransaction() 

        #assert trans.sender == "support@mysite.com"
        #assert msg.recipients == ["to@example.com"]


class TestAuthorisation(TestCase):

    pass

class TestPayments(TestCase):

    def test_process(self):

        trans = getValidExpressTransaction()

        trans = self.payments.setupRedirect(trans)

        print trans.paypal_express_token 
        print trans.redirect_url

         


