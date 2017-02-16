# -*- coding: utf-8 -*-


class WXPayError(Exception):
    """A WXPay error occurred."""


class WXPayCertError(Exception):
    """双向证书的接口， 为配置证书时抛出"""
