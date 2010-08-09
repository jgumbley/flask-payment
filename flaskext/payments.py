# -*- coding: utf-8 -*-
"""
    flaskext.payments
    ~~~~~~~~~~~~~~~~~

    Generic Payment gateway classes for Flask Payment
    May be dirtied with Paypal classes in the first instance

    :copyright: (c) 2010 by jgumbley.
    :license: BSD, see LICENSE for more details.
"""

class PaymentsConfigurationError(Exception): pass
class PaymentsValidationError(Exception): pass
class PaymentsErrorFromGateway(Exception): pass

class Payments(object):
    """
    Manages payment processing

    :param app: Flask instance

    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes payment gateway from the application settings.

        You can use this if you want to set up your Payment instance
        at configuration time.

        Binds to a specific implementation class based on the value
        in the PAYMENTS_API config value. 

        :param app: Flask application instance

        """
        # initialise gateway based on configuration
        self._init_gateway(app)
       
        self.testing = app.config['TESTING']
        self.app = app # this Payments instance reference to the Flask app

    def _init_gateway(self, app):
        """what i'm trying to do here is have some logic to conditionally
        instantiate a "payment gateway" member depending on the configuration
        of the PAYMENT_API configuration parameter.
        
        want to fail early if gateway not properly configured, so the idea
        is to delegate to the payment gateway class at this point to give it
        to the opptunity to validate its configuration and fail if needs be.
        """
        gateways =  {    'PayPal' : PayPalGateway 
                    }
        try:
            self.gateway = gateways[app.config['PAYMENT_API']](app)
        except KeyError:
            raise PaymentsConfigurationError

            
    def setupRedirect(self, trans):
        """Some gateways such as PayPal WPP Express Checkout and Google payments
        require you to redirect your customer to them first to collect info, 
        so going to make an explict getRedirect method for these instances.

        Returns the transaction with the redirect url attached. I guess the idea
        is the app stuffs this in the session and when it gets the user back
        will call authorise using this transaction.
        """
        if trans.validate(): # generic gateway abstract validation 
            return self.gateway.setupRedirect(trans) # gateway implementation does own
        else: raise PaymentTransactionValidationError()


    def authorise(self, trans):
        """Returns a valid authorisation (accepted or declined) or an error,
        which can be application (i.e. validation) or a system error (i.e. 500).
        
        The transaction is subject to gernic validatation, i.e. does it have
        necessary fields and do they add up, and only if valid will the
        instantiated gateway be invoked.

        """
        if trans.validate(): # generic gateway abstract validation 
            return self.gateway.authorise(trans) # gateway implementation does own
        else: raise PaymentTransactionValidationError()


class Transaction(object):
    """The payment request value object, with some validation logic
    It look like the way this is going the various gateways will be able to add
    whatever they like to this as and when they want.

    Not sure whether to subclass this and use some kind of factory so the app
    will get the right one depending on how they've instantiated Payments.
    """

    def validate(self):
        """
        validate the details of the payment, i.e. run regex on credit card
        number, ensure all required fields are filled etc.
        
        """
        return True


    def __init__(self):
        self.authorised = False
        pass

# ------------------------------------------------------------------------

import urllib, datetime

class PayPalGateway:
    """ Specific Impementation for PayPal WPP"""
    
    def __init__(self, app):
        # Need to catch value error and throw as config error
        try:
            self._init_API(app)
        except KeyError:
            raise PaymentsConfigurationError
            
    def _init_API(self ,app):
        """ initialises any stuff needed for the payment gateway API and should
        fail if anything is invalid or missing
        """
        self.signature_values = {
        'USER' : app.config['PAYPAL_API_USER'], 
        'PWD' : app.config['PAYPAL_API_PWD'],
        'SIGNATURE' : app.config['PAYPAL_API_SIGNATURE'],
        'VERSION' : '54.0',
        }
        self.API_ENDPOINT = app.config['PAYPAL_API_ENDPOINT']
        self.PAYPAL_URL =  app.config['PAYPAL_API_URL']
        self.signature = urllib.urlencode(self.signature_values) + "&"

    def setupRedirect(self, trans):
        """ this is for WPP only"""
        if trans.type == 'Express':
            return self._setupExpressTransfer(trans)
        else:
            raise PaymentTransactionValidationError()

    # why is this two methods surely this could be easier?

    def _setupExpressTransfer(self, trans):
        """ add details to transaction to allow it to be forwarded to the 
        third party gateway 
        """
        r = self.SetExpressCheckout(
                trans.amount,
                trans.return_url,
                trans.cancel_url
                )
        trans.paypal_express_token = urllib.unquote(r)
        
        trans.redirect_url = self.PAYPAL_URL + trans.paypal_express_token             
        return trans

    # Public methods of gateway 'interface'
    def authorise(self, trans):
        """Examines the type of transaction passed in and delegates to either
        the express payments flow or the direct payments flow, where further
        validation can take place.

        If its not a type of transaction which this gateway can process then it
        will throw its dummy out of the pram.
        """
        if trans.type == 'Express':
            return self._authoriseExpress(trans)
        elif trans.type == 'Direct':
            pass # not implemented yet
        else: raise PaymentTransactionValidationError()

    def _authoriseExpress(self, trans):
        """ calls authorise on payment setup via redirect to paypal
        """
        trans._raw = self.DoExpressCheckoutPayment(trans.paypal_express_token,
                trans.pay_id, trans.amount)  
        trans.authorised = True 
        return trans

    # API METHODS

    # PayPal python NVP API wrapper class.
    # This is a sample to help others get started on working
    # with the PayPal NVP API in Python. 
    # This is not a complete reference! Be sure to understand
    # what this class is doing before you try it on production servers!
    # ...use at your own peril.

    ## see https://www.paypal.com/IntegrationCenter/ic_nvp.html
    ## and
    ## https://www.paypal.com/en_US/ebook/PP_NVPAPI_DeveloperGuide/index.html
    ## for more information.

    # by Mike Atlas / LowSingle.com / MassWrestling.com, September 2007
    # No License Expressed. Feel free to distribute, modify, 
#  and use in any open or closed source project without credit to the author

    def SetExpressCheckout(self, amount, return_url, cancel_url):
        params = {
            'METHOD' : "SetExpressCheckout",
            'NOSHIPPING' : 1,
            'PAYMENTACTION' : 'Authorization',
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url, 
            'AMT' : amount,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_token = ""
        for token in response.split('&'):
            if token.find("TOKEN=") != -1:
                response_token = token[ (token.find("TOKEN=")+6):]
        return response_token
    
    def DoExpressCheckoutPayment(self, token, payer_id, amt):
        params = {
            'METHOD' : "DoExpressCheckoutPayment",
            'PAYMENTACTION' : 'Sale',
            'RETURNURL' : 'http://www.yoursite.com/returnurl', #edit this 
            'CANCELURL' : 'http://www.yoursite.com/cancelurl', #edit this 
            'TOKEN' : token,
            'AMT' : amt,
            'PAYERID' : payer_id,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
                response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens
    

    # Get info on transaction
    def GetTransactionDetails(self, tx_id):
        params = {
            'METHOD' : "GetTransactionDetails", 
            'TRANSACTIONID' : tx_id,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
                response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens
   
    # Direct payment
    def DoDirectPayment(self, amt, ipaddress, acct, expdate, cvv2, firstname, lastname, cctype, street, city, state, zipcode):
        params = {
            'METHOD' : "DoDirectPayment",
            'PAYMENTACTION' : 'Sale',
            'AMT' : amt,
            'IPADDRESS' : ipaddress,
            'ACCT': acct,
            'EXPDATE' : expdate,
            'CVV2' : cvv2,
            'FIRSTNAME' : firstname,
            'LASTNAME': lastname,
            'CREDITCARDTYPE': cctype,
            'STREET': street,
            'CITY': city,
            'STATE': state,
            'ZIP':zipcode,
            'COUNTRY' : 'United States',
            'COUNTRYCODE': 'US',
            'RETURNURL' : 'http://www.yoursite.com/returnurl', #why needed? 
            'CANCELURL' : 'http://www.yoursite.com/cancelurl', # ditto
            'L_DESC0' : "Desc: ",
            'L_NAME0' : "Name: ",
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens
