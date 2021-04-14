# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import text_type


class PaymentnepalCallback(object):

    def __init__(self, services):
        """
        services - services list
        """
        self.services = {
            text_type(service.service_id): service for service in services
        }

    def handle(self, post):
        """
        Callback handling
        """
        if 'service_id' not in post:
            raise PaymentnepalException(
                'No required param service_id')

        if post['service_id'] in self.services:
            service = self.services[post['service_id']]
            if service.check_callback_sign(post):
                self.callback(post)
            else:
                raise PaymentnepalException("Sign validation error")
        else:
            raise PaymentnepalException(
                "Unknown service: %s" % type(post['service_id']))

    def callback(self, data):
        """
        Handling a callback after sign validation
        """
        if data['command'] == 'process':
            self.callback_process(data)
        elif data['command'] == 'success':
            self.callback_success(data)
        elif data['command'] == 'recurrent_cancel':
            self.callback_recurrent_cancel(data)
        elif data['command'] == 'refund':
            self.callback_refund(data)
        else:
            raise PaymentnepalException(
                "Unexpected command type: %s" % data['command'])

    def callback_process(self, data):
        """
        Callback for any (including partial) payment
        """
        pass

    def callback_success(self, data):
        """
        Callback for full payment
        """

    def callback_recurrent_cancel(self, data):
        """
        Called when customer has cancelled recurrent payments
        """
        pass

    def callback_refund(self, data):
        """
        Refund result callback
        """
        pass
