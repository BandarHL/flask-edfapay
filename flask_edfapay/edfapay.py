import hashlib
import requests
from typing import Optional
from flask import Flask
from teritorio.main import Currencies, Currency
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PaymentPayload:
    order_id: str
    order_amount: str
    order_currency: str
    order_description: str
    payer_first_name: str
    payer_last_name: str
    payer_address: str
    payer_country: str
    payer_city: str
    payer_zip: str
    payer_email: str
    payer_phone: str
    payer_ip: str
    term_url_3ds: str


class EdfaPay:
    def __init__(self, app: Optional[Flask] = None):
        self.merchant_id = None
        self.merchant_password = None
        self.currencies = Currencies()

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.merchant_id = app.config['EDFAPAY_MERCHANT_ID']
        self.merchant_password = app.config['EDFAPAY_MERCHANT_PASSWORD']

    def create_payment_url(self, payment_payload: PaymentPayload):
        """
        Create a payment URL for customer.
        :param payment_payload: Payment payload.
        :return: Payment json response for customer.
        """
        payload = {
            'action': 'SALE',
            'req_token': 'N',
            'auth': 'N',
            'recurring_init': 'N'
        }
        if not self.merchant_id or not self.merchant_password or not payment_payload:
            raise Exception('merchant_id or merchant_password or payment_payload is not provided.')

        try:
            currency: Currency = self.currencies[payment_payload.order_currency]
            formatted_price = self.format_price(currency, payment_payload.order_amount)
            generated_hash = self.generate_hash_session(payment_payload.order_id, formatted_price,
                                                        currency.code, payment_payload.order_description,
                                                        self.merchant_password)
            payload.update({
                'edfa_merchant_id': self.merchant_id,
                'order_id': payment_payload.order_id,
                'order_amount': formatted_price,
                'order_currency': currency.code,
                'order_description': payment_payload.order_description,
                'payer_first_name': payment_payload.payer_first_name,
                'payer_last_name': payment_payload.payer_last_name,
                'payer_address': payment_payload.payer_address,
                'payer_country': payment_payload.payer_country,
                'payer_city': payment_payload.payer_city,
                'payer_zip': payment_payload.payer_zip,
                'payer_email': payment_payload.payer_email,
                'payer_phone': payment_payload.payer_phone,
                'payer_ip': payment_payload.payer_ip,
                'term_url_3ds': payment_payload.term_url_3ds,
                'hash': generated_hash
            })
        except Exception as e:
            raise e

        response = requests.post('https://api.edfapay.com/payment/initiate', data=payload)
        if response.status_code != 200:
            raise Exception('Failed to initiate payment. Details: {}'.format(response.text))

        return response.json()

    def transaction_status(self, order_id, payment_id):
        """
        Transaction status of specific payment.
        :param order_id: Order id
        :param payment_id: Payment id
        :return: Transaction full status of payment
        """
        payload = {}
        if not self.merchant_id or not self.merchant_password or not order_id or not payment_id:
            raise Exception('merchant_id or merchant_password or order_id or payment_id is not provided.')

        try:
            generated_hash = self.generate_hash_session(payment_id, self.merchant_password)
            payload.update({
                'order_id': order_id,
                'merchant_id': self.merchant_id,
                'gway_Payment_id': payment_id,
                'hash': generated_hash
            })
        except Exception as e:
            raise e

        response = requests.post('https://api.edfapay.com/payment/status', data=payload)
        if response.status_code != 200:
            raise Exception('Failed to check the payment status. Details: {}'.format(response.text))

        return response.json()

    @classmethod
    def generate_hash_session(cls, *args) -> str:
        """
        Special signature to validate your request to Payment Platform Addition in Signature section.
        """
        to_md5 = ''
        for arg in args:
            to_md5 += str(arg).upper()
        md5_hash = hashlib.md5(to_md5.encode()).hexdigest()
        sha1_hash = hashlib.sha1(md5_hash.encode()).hexdigest()
        return sha1_hash

    @classmethod
    def format_price(cls, currency: Currency, price: str) -> Decimal:
        """
        Format price for based on currency decimal places
        :param currency: Currency to format
        :param price: Price to format
        :return: Formatted price
        """
        decimal_places = currency.minor_units
        formatted_price = Decimal(price).quantize(Decimal('1.' + '0' * decimal_places))

        return formatted_price
