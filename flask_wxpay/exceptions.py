# -*- coding: utf-8 -*-


class WXPayError(Exception):
    """A WXPay error occurred."""


class CertError(WXPayError):
    """双向证书的接口， 使用证书的接口如果未配置证书时抛出"""


class NotifyError(WXPayError):
    """支付通知相关的错误"""
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return self.msg


class NotifySignError(NotifyError):
    """支付通知签名错误"""
    def __init__(self):
        msg = '签名错误'
        super(NotifySignError, self).__init__(msg)


class NotifyReturnError(NotifyError):
    """支付通知return_code为FAIL时"""
    def __init__(self, return_msg, msg=''):
        self.return_msg = return_msg
        if not msg:
            self.msg = return_msg


class NotifyResultError(NotifyError):
    """支付通知result_code为FAIL时
    属性: err_code, err_code_des
    """
    def __init__(self, err_code, err_code_des, msg=''):
        self.err_code = err_code
        self.err_code_des = err_code_des
        if not msg:
            self.msg = err_code_des

    def __str__(self):
        return 'err_code: {}, err_code_des: {}'.format(self.err_code,
                                                       self.err_code_des)
