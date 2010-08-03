# -*- coding: utf-8 -*-
"""
    flaskext.payments
    ~~~~~~~~~~~~~~~~~

    Description of the module goes here...

    :copyright: (c) 2010 by jgumbley.
    :license: BSD, see LICENSE for more details.
"""

class PaymentValidationError(Exception): pass

class PaymentWebserviceSystemError(Exception): pass

class Payments(object):
    """
    Manages payment processing

    :param app: Flask instance

    """

    def __init__(self, app=None):
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initializes payment gateway config from the application
        settings.

        You can use this if you want to set up your Payment instance
        at configuration time.

        :param app: Flask application instance
        """
        
        # here is the pattern for defaults:
        # port = app.config.get('MAIL_PORT', 25)

        self.testing = app.config['TESTING']

        self.app = app

    def process(self, trans):
        return Authorisation()

class Transaction(object):
    """

    """
    
    def __init__(self, params):
        pass

class Authorisation(object):
    """

    """

    status = False

    pass


