from datetime import datetime
from flask import Flask, session, request, flash, url_for, redirect, \
     render_template, abort
from flaskext.payments import Payments, Transaction

app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
app.config.from_pyfile('../yourpaypal.settings')

payments = Payments(app)

@app.route('/')
def show_all():
    return render_template('checkout.html')

@app.route('/paypal-express')
def paypal_express_checkout():
    trans = Transaction()
    trans.type = 'Express'
    trans.amount = 100
    trans.return_url = 'http://localhost:5000/paypal-express-complete'
    trans.cancel_url = 'http://localhost:5000/paypal-express-cancel'

    trans = payments.setupRedirect(trans)
    session['trans'] = trans
    
    return redirect(trans.redirect_url)

@app.route('/paypal-express-complete')
def paypal_express_complete():
    trans = session['trans']
    payerid = request.values['PayerID'] 
    trans.pay_id = payerid

    trans = payments.authorise(trans)
    session['trans'] = trans

    return redirect('/confirm')

@app.route('/paypal-direct-payments')
def paypal_direct_payments():
    return render_template('fill_in_details.html')

@app.route('/confirm')
def confirm():
    trans = session['trans']
    return render_template('confirmation.html', trans=trans)

if __name__ == '__main__':
    app.run()
