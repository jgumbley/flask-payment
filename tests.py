# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest

from flask import Flask, g
from flaskext.payments import Payments, Transaction, PaymentTransactionValidationError

class PaymentsTestCase(unittest.TestCase):
    """Base class for test cases for Flask Payments 
    """
    TESTING = True

    # Which gateway implementation class to bind to for payments specified in 
    # configuration, and bound at startup.
    PAYMENT_API = None
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(self)

        self.loadPrivateConfig()

        self.payments = Payments(self.app)
        
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

class PayPalTestCase(PaymentsTestCase):
    """ Extending this PaymentsTestCase with PayPal specific configurations
    """
    PAYMENT_API = 'PayPal'

    # Define PayPal Specific Stuff
    PAYPAL_API_ENDPOINT = 'https://api-3t.sandbox.paypal.com/nvp'
    PAYPAL_API_URL = 'https://www.sandbox.paypal.com/webscr&cmd=_express-checkout&token='

    def loadPrivateConfig(self):
        # need to keep personal API details out of scm
        self.app.config.from_pyfile('yourpaypal.settings')


def getValidWPPExpressTransaction():
    """Convenience helper to get a valid WPP Express Transaction as a starting
    point
    """
    trans = Transaction()
    trans.type = 'Express'
    trans.amount = 100
    trans.return_url = 'http://www.jgumbley.com'
    trans.cancel_url = 'http://www.jgumbley.com'
    return trans

import webbrowser
class WalkingSkeleton(PayPalTestCase):
    """These tests are not really unit tests as such they are just designed to test
    the flow from end to end, before drilling into all the specific possibilities
    and conditions
    """
    def test_express_payment(self):
        """Test end to end we can process an Express Payment in the Sandbox
        """ 
        trans = getValidWPPExpressTransaction()
        
        trans = self.payments.setupRedirect(trans)
        
        # this seems pretty unconventional for a test
        # but we need to dump the user at the paypal site so they can validate
        # the token
        webbrowser.open(trans.redirect_url)
        # and there doesn't seem to be a way to mock that out, so really need to
        # do this and accept input back from the tester
        trans.pay_id = raw_input(">")
        
        # now call authorise
        trans = self.payments.authorise(trans)
        print trans._raw
        assert trans.authorised == False
