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
        """Initializes payment gateway config from the application
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
        """The transaction is validated and only if valid will the appropriate
        webservice be invoked.

        """
        if trans.validate():
            return self._doPayPal()
        else: raise PaymentTransactionValidationError()

    def _doPayPal(self):
        auth = Authorisation()
        pp = PayPal(    self.app.config['PAYPAL_API_USER'],
                        self.app.config['PAYPAL_API_PWD'],
                        self.app.config['PAYPAL_API_SIGNATURE'],
                        self.app.config['PAYPAL_API_ENDPOINT'],
                        self.app.config['PAYPAL_API_URL']
                        )
        pp_token = pp.SetExpressCheckout(20)
        auth.express_token = pp.GetExpressCheckoutDetails(pp_token)
        auth.url= self.app.config['PAYPAL_API_URL'] 
        return auth



class Transaction(object):
    """The payment request value object, with some validation logic
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
    """The payment response value object
    
    Status will be true if payment processed OK and False otherwise
    other details about transaction outcome attached to this DTO

    """

    status = False

# ------------------------------------------------------------------------


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

# Example usage: ===============
#    paypal = PayPal()
#    pp_token = paypal.SetExpressCheckout(100)
#    express_token = paypal.GetExpressCheckoutDetails(pp_token)
#    url= paypal.PAYPAL_URL + express_token
#    HttpResponseRedirect(url) ## django specific http redirect call for payment


import urllib, md5, datetime

class PayPal:
    """ #PayPal utility class"""
    
    def __init__(self, usr, pwd, sig, endpoint, url):
        self.signature_values = {
        'USER' : usr, 
        'PWD' : pwd,
        'SIGNATURE' : sig,
        'VERSION' : '53.0',
        }
        self.API_ENDPOINT = endpoint
        self.PAYPAL_URL = url 
        self.signature = urllib.urlencode(self.signature_values) + "&"

    # API METHODS
    def SetExpressCheckout(self, amount):
        params = {
            'METHOD' : "SetExpressCheckout",
            'NOSHIPPING' : 1,
            'PAYMENTACTION' : 'Authorization',
            'RETURNURL' : 'http://www.jgumbley.com/returnurl', #edit this 
            'CANCELURL' : 'http://www.jgumbley.com/cancelurl', #edit this 
            'AMT' : amount,
        }

        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_token = ""
        for token in response.split('&'):
            if token.find("TOKEN=") != -1:
                response_token = token[ (token.find("TOKEN=")+6):]
        return response_token
    
    def GetExpressCheckoutDetails(self, token):
        params = {
            'METHOD' : "GetExpressCheckoutDetails",
            'RETURNURL' : 'http://www.jgumbley.com/returnurl', #edit this 
            'CANCELURL' : 'http://www.jgumbley.com/cancelurl', #edit this 
            'TOKEN' : token,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        return response_tokens
    
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
                
    def MassPay(self, email, amt, note, email_subject):
        unique_id = str(md5.new(str(datetime.datetime.now())).hexdigest())
        params = {
            'METHOD' : "MassPay",
            'RECEIVERTYPE' : "EmailAddress",
            'L_AMT0' : amt,
            'CURRENCYCODE' : 'USD',
            'L_EMAIL0' : email,
            'L_UNIQUE0' : unique_id,
            'L_NOTE0' : note,
            'EMAILSUBJECT': email_subject,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
                response_tokens[key] = urllib.unquote(response_tokens[key])
        response_tokens['unique_id'] = unique_id
        return response_tokens
                
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
            'RETURNURL' : 'http://www.yoursite.com/returnurl', #edit this 
            'CANCELURL' : 'http://www.yoursite.com/cancelurl', #edit this 
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
