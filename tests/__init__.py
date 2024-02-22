from flask import Flask
from flask_edfapay import EdfaPay

app = Flask(__name__)
app.config["EDFAPAY_MERCHANT_ID"] = "MERCHANT_ID"
app.config["EDFAPAY_MERCHANT_PASSWORD"] = "MERCHANT_PASSWORD"
pay_engine = EdfaPay(app)


@app.route('/')
def hello():
    return 'Hello, Flask!'
