# -*- coding: utf-8 -*-


class WXPayError(Exception):
    """A WXPay error occurred."""


class CertError(WXPayError):
    """双向证书的接口， 使用证书的接口如果未配置证书时抛出"""


class ReturnCodeFail(WXPayError):
    """return_code为FAIL时"""

    def __init__(self, return_msg):
        self.return_msg = return_msg

    def str(self):
        return 'return_code: FAIL, return_msg: {}'.foramt(self.return_msg)


class ResultCodeFail(WXPayError):
    """result_code为FAIL时
    属性: err_code, err_code_des
    """

    def __init__(self, err_code, err_code_des):
        self.err_code = err_code
        self.err_code_des = err_code_des

    def __str__(self):
        return 'result_code: FAIL, err_code: {}, err_code_des: {}'.format(
            self.err_code,
            self.err_code_des)


class SignError(WXPayError):
    """签名错误"""
