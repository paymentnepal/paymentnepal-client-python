# -*- coding: utf-8 -*-


class PaymentnepalException(Exception):
    def __init__(self, message, errors=None):
        super(PaymentnepalException, self).__init__(message)
        self.errors = errors or {}


class UniqueError(PaymentnepalException):
    pass


class AuthError(PaymentnepalException):
    pass


class MissArgumentError(PaymentnepalException, ValueError):
    pass


CODE2EXCEPTION = {
    'unknown': PaymentnepalException,
    'common': PaymentnepalException,
    'unique': UniqueError,
    'auth': AuthError,
}
