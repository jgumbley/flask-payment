# -*- coding: utf-8 -*-
"""
    flaskext.payments
    ~~~~~~~~~~~~~~~~~

    Generic Payment gateway classes for Flask Payment
    May be dirtied with Paypal classes in the first instance

    :copyright: (c) 2010 by jgumbley.
    :license: BSD, see LICENSE for more details.
"""

class PaymentGatewayNotProperlyInitialisedError(Exception): pass

class PaymentTransactionNotValidForConfiguredGatewayError(Exception): pass

class PaymentTransactionValidationError(Exception): pass

class PaymentWebServiceSystemError(Exception): pass

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
        # port = 
        # app.config.get('MAIL_PORT', 25)
        
        # want to fail early if gateway not properly configured
        if False:
            raise PaymentGatewayNotProperlyInitialisedError(Exception)
        
        self.testing = app.config['TESTING']

        self.app = app

    def process(self, trans):
        """
        The transaction is validated and only if valid will the appropriate
        webservice be invoked.

        """
        if trans.validate():
            return Authorisation()        
        else: raise PaymentTransactionValidationError()

class Transaction(object):
    """
    the payment request value object, with some validation logic
    """

    def validate(self):
        """
        validate the details of the payment, i.e. run regex on credit card
        number, ensure all required fields are filled etc.
        
        """
        return True
    
    def __init__(self, params):
        pass

class Authorisation(object):
    """
    the payment response value object
    
    status will be true if payment processed OK and False otherwise
    other details about transaction outcome attached to this DTO

    """

    status = False



