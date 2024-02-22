from unittest import TestCase
from tests import app, pay_engine
from flask_edfapay import PaymentPayload
import re


class TestEdfaPay(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_create_payment_url(self):
        customer_payload = PaymentPayload('ORDER0015', '1', 'SAR', 'test', 'Bandar', 'Alruwaili',
                                          'test@gmail.com', 'SA', 'Quryyat', '77777',
                                          'test@gmail.com', '966111111111', '95.219.198.203',
                                          'https://test.com')
        payment_checkout_url = pay_engine.create_payment_url(payment_payload=customer_payload)
        self.assertRegex(payment_checkout_url.get('redirect_url'), re.compile(r'^https://'))
