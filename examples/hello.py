from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flaskext.payments import Payments, Transaction

app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
payments = Payments(app)

@app.route('/')
def show_all():
    return render_template('checkout.html')

@app.route('/paypal-express')
def paypal_express_checkout():
    trans = Transaction()
    trans.type = 'Express'
    trans.amount = 100
    trans.return_url = 'http://www.jgumbley.com'
    trans.cancel_url = 'http://www.jgumbley.com'

    trans = self.payments.setupRedirect(trans)
    
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run()
