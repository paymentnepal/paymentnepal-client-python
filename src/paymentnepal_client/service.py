# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests
import hashlib
import json

from six import text_type

from .exceptions import CODE2EXCEPTION, MissArgumentError, PaymentnepalException
from .sign import sign


class PaymentnepalService(object):
    FIRST_CONNECTION_PROFILE = {
        'base_url': 'https://pay.paymentnepal.com/',
        'card_token_url': 'https://secure.paymentnepal.com/cardtoken/',
        # 'card_token_test_url': 'https://test.rficb.ru/cardtoken/'
    }
    SECOND_CONNECTION_PROFILE = {
        'base_url': 'https://pay.paymentnepal.com/',
        'card_token_url': 'https://secure.paymentnepal.com/cardtoken/',
        # 'card_token_test_url': 'https://test.rficb.ru/cardtoken/'
    }

    def __init__(self, service_id, secret, connection_profile=None,
                 logger=None):
        """
        secret - secret_key from service settings
        """
        self.service_id = service_id
        self.secret = secret
        if not connection_profile:
            self.connection_profile = self.FIRST_CONNECTION_PROFILE
        else:
            self.connection_profile = connection_profile
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def _request(self, url, method, data):
        try:
            self.logger.debug('Sent {} request with params {}'
                              .format(method.upper(), data))

            if method == 'get':
                response = requests.get(url, params=data)
            else:
                response = requests.post(url, data)

            if response.status_code != 200:
                self.logger.debug(u'Server unavailable: {}'
                                  .format(response.status_code))
                raise PaymentnepalException('Сервер не доступен: {}'
                                            .format(response.status_code))
        except requests.ConnectionError as e:
            raise PaymentnepalException(e)

        content = response.content.decode('utf-8')
        self.logger.debug('Server response: {}'.format(content))

        json_response = json.loads(content)
        if json_response['status'] == 'error':
            msg = json_response.get('msg', json_response.get('message'))
            code = json_response.get('code', 'unknown')
            errors = json_response.get('errors')
            raise CODE2EXCEPTION.get(code, PaymentnepalException)(
                msg, errors=errors)

        return json_response

    def _get(self, url, data=None):
        return self._request(url, 'get', data)

    def _post(self, url, data=None):
        return self._request(url, 'post', data)

    def pay_types(self):
        """
        Getting list of payment methods available
        """
        check = hashlib.md5(
            (text_type(self.service_id) + self.secret).encode('utf-8'))
        check = check.hexdigest()
        url = ("%salba/pay_types/?service_id=%s&check=%s" %
               (self.connection_profile['base_url'], self.service_id, check))
        return self._get(url)['types']

    def init_payment(self, pay_type, cost, name, email, phone,
                     order_id=None, comment=None, bank_params=None,
                     commission=None, card_token=None, recurrent_params=None,
                     **kwargs):
        """
        Init payment
        pay_type - payment type from payment methods list
        cost - payment amount
        name - payment name (for example 'Headphones JBL-00003')
        email - customer email
        order_id - unique id for order
        comment - random comment for payment (addinfo)
        bank_params - requisites params for bank transfer
        commission - points who pays fee
          values available: 'partner', 'abonent'
        """
        fields = {
            "cost": cost,
            "name": name,
            "email": email,
            "phone_number": phone,
            "background": "1",
            "type": pay_type,
            "service_id": self.service_id,
            "version": "2.0"
        }
        if order_id:
            fields['order_id'] = order_id
        if comment:
            fields['comment'] = comment
        if bank_params:
            for bkey, bval in bank_params.items():
                fields[bkey] = bval
        if commission:
            fields['commission'] = commission
        if card_token:
            fields['card_token'] = card_token
        if recurrent_params:
            fields['recurrent_params'] = recurrent_params

        fields.update(kwargs)

        url = self.connection_profile['base_url'] + "alba/input/"
        fields['check'] = sign("POST", url, fields, self.secret)

        return self._post(url, fields)

    def transaction_details(self, tid=None, order_id=None):
        """
        Getting transaction info
        tid - transaction id in billing
        """
        if tid:
            params = {'tid': tid}
        elif order_id:
            params = {'order_id': order_id, 'service_id': self.service_id}
        else:
            raise MissArgumentError('Agrs tid or order_id expected')

        url = self.connection_profile['base_url'] + "alba/details/"
        params['version'] = '2.0'
        params['check'] = sign("POST", url, params, self.secret)
        answer = self._post(url, params)
        return answer

    def refund(self, tid, amount=None, test=False, reason=None):
        """
        проведение возврата
        """
        url = self.connection_profile['base_url'] + "alba/refund/"
        fields = {'version': '2.0',
                  'tid': tid}
        if amount:
            fields['amount'] = amount

        if test:
            fields['test'] = '1'

        if reason:
            fields['reason'] = reason

        fields['check'] = sign("POST", url, fields, self.secret)
        answer = self._post(url, fields)
        return answer

    def gate_details(self, gate):
        """
        Getting gateway info
        gate - gate short_name
        """
        url = self.connection_profile['base_url'] + "alba/gate_details/"
        params = {'version': '2.0',
                  'gate': gate,
                  'service_id': self.service_id}
        params['check'] = sign("GET", url, params, self.secret)
        answer = self._get(url, params)
        return answer

    def check_callback_sign(self, post):
        """
        Callback handling
        array $post - $_POST params array
        """
        order = ['tid', 'name', 'comment', 'partner_id', 'service_id',
                 'order_id', 'type', 'cost', 'income_total', 'income',
                 'partner_income', 'system_income', 'command', 'phone_number',
                 'email', 'resultStr', 'date_created', 'version']
        params = [post.get(field, '') for field in order]
        params.append(self.secret)
        digest_hash = hashlib.md5(
            (''.join(params)).encode('utf-8')).hexdigest()
        return digest_hash == post['check']

    def create_card_token(
            self, card, exp_month, exp_year, cvc, test,
            card_holder=None):
        month = exp_month
        if len(month) == 1:
            month = '0' + month

        params = {
            'service_id': self.service_id,
            'card': card,
            'exp_month': month,
            'exp_year': exp_year,
            'cvc': cvc
        }
        if card_holder:
            params.update({'card_holder': card_holder})

        url = (self.connection_profile['card_token_test_url'] if test
               else self.connection_profile['card_token_url'])
        result = self._post(url + 'create', params)
        return result['token']

    def cancel_recurrent_payment(self, order_id):
        url = self.connection_profile['base_url'] + 'alba/recurrent_change/'
        fields = {
            'operation': 'cancel',
            'order_id': order_id,
            'service_id': self.service_id,
            'version': '2.0'
        }
        fields['check'] = sign('POST', url, fields, self.secret)
        return self._post(url, fields)
