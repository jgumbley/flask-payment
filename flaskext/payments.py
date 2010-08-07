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
        """Initializes payment gateway from the application settings.

        You can use this if you want to set up your Payment instance
        at configuration time.

        Binds to a specific implementation class based on the value
        in the PAYMENTS_API config value. 

        :param app: Flask application instance

        """
        # here is the pattern for defaults:
        # app.config.get('MAIL_PORT', 25)
       
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
        self.payment_api = app.config['PAYMENT_API']
        
        if self.payment_api == 'PayPal':
            self.gateway = PayPalGateway(app)
        else:
            raise PaymentGatewayNotProperlyInitialisedError(Exception)

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
        which can be application or a system error.
        
        The transaction is subject to gernic validatation, i.e. does it have
        necessary fields and do they add up, and only if valid will the
        instantiated gateway be invoked.

        """
        if trans.validate(): # generic gateway abstract validation 
            return self.gateway.authorise(trans) # gateway implementation does own
        else: raise PaymentTransactionValidationError()


class Transaction(object):
    """The payment request value object, with some validation logic
    """

    def validate(self):
        """
        validate the details of the payment, i.e. run regex on credit card
        number, ensure all required fields are filled etc.
        
        """
        return True


    def __init__(self):
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


import urllib, datetime

class PayPalGateway:
    """ #PayPal utility class"""
    
    def __init__(self, app):
        # Need to catch value error and throw as config error
        try:
            self._init_API(app)
        except ValueError:
            raise PaymentGatewayNotProperlyInitialisedError(Exception)
            
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
        try:
            if trans.type == 'Express':
                try:
                    return self._setupExpressTransfer(trans)
                except:
                    raise PaymentWebserviceSystemError() 
            else:
                raise PaymentTransactionValidationError()
        except AttributeError:
            raise PaymentTransactionValidationError()


    def _setupExpressTransfer(self, trans):
        """ add details to transaction to allow it to be forwarded to the 
        third party gateway 
        """
        trans.paypal_express_token = self.SetExpressCheckout(trans.amount)
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
        try:
            if trans.type == 'Express':
                return self._processExpress(trans)
            elif trans.type == 'Direct':
                pass # not implemented yet
            else: raise PaymentTransactionValidationError()
        except AttributeError:
            raise PaymentTransactionValidationError()


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
