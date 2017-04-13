# -*- coding: utf-8 -*-
"""微信支付的flask扩展"""

__version__ = '0.1.7'  # noqa

from datetime import datetime, timedelta
import time
import json
import requests

import httpdns

from .utils import gen_random_str, md5, dict_to_xml, xml_to_dict, now_str  # noqa
from .exceptions import (
    WXPayError, CertError, ReturnCodeFail, ResultCodeFail, SignError)


class WXPay(object):
    """微信支付类"""

    def __init__(self, app=None):
        self.api_host = 'api.mch.weixin.qq.com'
        self.scheme = 'https'
        self.api_host_ip = httpdns.get_ip(self.api_host)
        self.timeout = 10

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.appid = app.config['WX_APPID']
        self.sandbox = app.config.get('WXPAY_SANDBOX', False)
        self.mch_id = app.config['WXPAY_MCHID']
        self.key = app.config['WXPAY_KEY']
        self.notify_url = app.config['WXPAY_NOTIFY_URL']

        self.cert_path = app.config.get('WXPAY_CERT_PATH')
        self.cert_key_path = app.config.get('WXPAY_CERT_KEY_PATH')

    def _post(self, path, data, use_cert=False, check_result=True):
        """添加发送签名
        处理返回结果成dict, 并检查签名
        """
        base_data = dict(
            appid=self.appid,
            mch_id=self.mch_id,
            nonce_str=gen_random_str()
        )
        if path == '/mmpaymkttransfers/sendredpack':
            del base_data['appid']
        data.update(base_data)

        data['sign'] = self.get_sign(data)

        xml_data = dict_to_xml(data).encode('utf-8')
        if use_cert:
            if not (self.cert_path and self.cert_key_path):
                raise CertError()
            api_cert = (self.cert_path, self.cert_key_path)
        else:
            api_cert = None

        if self.sandbox:
            path = '/sandboxnew' + path
        for _ in range(3):
            try:
                url = '{0}://{1}{2}'.format(self.scheme,
                                            self.api_host_ip,
                                            path)
                r = requests.post(url, data=xml_data, timeout=self.timeout,
                                  verify=False, cert=api_cert,
                                  headers={'Host': self.api_host})
                if '<return_code>' not in r.text:
                    # 不是微信支付接口返回的数据, 重置ip
                    self.ip = httpdns.get_ip(self.api_host, force_update=True)
                    continue

                break
            except (requests.ConnectionError, requests.Timeout):
                self.api_host_ip = httpdns.get_ip(self.api_host,
                                                  force_update=True)
        if r.encoding == 'ISO-8859-1':
            r.encoding = 'UTF-8'
        xml = r.text
        data = xml_to_dict(xml)
        # 使用证书的接口不检查sign
        if check_result:
            check_sign = not use_cert
            self.check_data(data, check_sign)
        return data

    def get_sign(self, data):
        """生成签名"""
        # 签名步骤一: 按字典序排序参数
        items = sorted(data.items(), key=lambda x: x[0])
        # items.sort(key=lambda x: x[0])
        s = '&'.join('{0}={1}'.format(key, value) for key, value in items)
        # 签名步骤二: 在string后加入KEY
        s = '{0}&key={1}'.format(s, self.key)
        # 签名步骤三: MD5加密
        result = md5(s)
        # 签名步骤四: 所有字符转为大写
        return result.upper()

    def unified_order(self, out_trade_no, total_fee, ip, body, expire_seconds,
                      notify_url=None, trade_type='JSAPI', openid=None):
        """`统一下单
        <https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_1>`_

        :params out_trade_no: 商户订单号
        :params total_fee: 总金额，单位为分
        :params ip: 用户端实际ip
        :params body: 商品描述
        :params expire_seconds: 订单失效时间,最短失效时间间隔必须大于5分钟
        :params notify_url: 微信支付异步通知回调地址, 默认使用WXPAY_NOTIFY_URL的配置
        :params trade_type: JSAPI，NATIVE，APP, 默认值为JSAPI
        :params openid: 用户openid, trade_type为JSAPI时需要
        :rtype: dict
        """
        path = '/pay/unifiedorder'
        now = datetime.now()
        time_start = now.strftime('%Y%m%d%H%M%S')
        time_expire = (now + timedelta(seconds=expire_seconds))\
            .strftime('%Y%m%d%H%M%S')

        data = dict(
            body=body,
            notify_url=notify_url or self.notify_url,
            out_trade_no=out_trade_no,
            spbill_create_ip=ip,
            total_fee=total_fee,
            trade_type=trade_type,
            time_start=time_start,
            time_expire=time_expire
        )
        if trade_type == 'JSAPI':
            if not openid:
                raise WXPayError('微信内支付需要openid')
            data['openid'] = openid

        result = self._post(path, data)

        if result['return_code'] != 'SUCCESS':
            msg = '统一下单错误, msg-{0},\ndata-{1}' \
                .format(result['return_msg'], json.dumps(data))
            raise WXPayError(msg)

        return result

    def query_order(self, out_trade_no=None, transaction_id=None):
        """`查询订单
        <https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_2&index=4>`_
        """
        path = '/pay/orderquery'
        if not (transaction_id or out_trade_no):
            raise WXPayError('查询订单需要transaction_id or out_trade_no')
        data = dict()
        if transaction_id:
            data['transaction_id'] = transaction_id
        else:
            data['out_trade_no'] = out_trade_no

        return self._post(path, data)

    def close_order(self, out_trade_no):
        """`关闭订单
        <https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_3&index=5>`_
        """
        path = '/pay/closeorder'
        data = dict(out_trade_no=out_trade_no)
        return self._post(path, data)

    def refund(self, out_trade_no, out_refund_no, total_fee, refund_fee):
        """`退款 <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4>`_
        """
        path = '/secapi/pay/refund'
        data = dict(
            out_trade_no=out_trade_no,
            out_refund_no=out_refund_no,
            total_fee=total_fee,
            refund_fee=refund_fee,
            op_user_id=self.mch_id
        )
        return self._post(path, data, cert=True)

    def sendredpack(self, mch_billno, send_name, re_openid, total_amount,
                    wishing, client_ip, act_name, remark):
        """发红包

        :params mch_billno: 商户订单号
        :params send_name: 商户名称
        :params re_openid: 用户openid
        :params total_amount: 付款金额
        :params wishing: 红包祝福语
        :params client_ip: 调用接口的机器IP地址
        :params act_name: 活动名称
        :params remark: 备注信息
        """
        path = '/mmpaymkttransfers/sendredpack'
        data = dict(
            wxappid=self.appid,
            mch_billno=mch_billno,
            send_name=send_name,
            re_openid=re_openid,
            total_amount=total_amount,
            total_num=1,
            wishing=wishing,
            client_ip=client_ip,
            act_name=act_name,
            remark=remark
        )
        return self._post(path, data, cert=True, sendredpack=True)

    def get_redpack_info(self, mch_billno):
        """查询红包信息
        :param mch_billno: 商户订单号
        """
        path = '/mmpaymkttransfers/gethbinfo'
        data = dict(
            mch_billno=mch_billno,
            bill_type='MCHT'
        )
        return self._post(path, data, cert=True)

    def get_sign_key(self):
        """获取验签秘钥，沙箱环境下有效"""
        path = '/pay/getsignkey'
        data = dict()
        return self._post(path, data, check_result=False)

    def get_app_prepay_data(self, prepay_id):
        """返回给客户端的prepay数据

        :params prepay_id: :meth:`unified_order` 接口获取到的prepay_id
        :return: prepay data
        :rtype: dict
        """
        data = dict(
            appid=self.appid,
            noncestr=gen_random_str,
            package='Sign=WXPay',
            partnerid=self.mch_id,
            prepayid=prepay_id,
            timestamp=str(int(time.time()))
        )
        data['sign'] = self.get_sign(data)
        return data

    def get_jsapi_prepay_data(self, prepay_id):
        """返回给公众号的prepay数据

        :params prepay_id: :meth:`unified_order` 接口获取到的prepay_id
        :return: prepay data
        :rtype: dict
        """
        data = dict(
            appId=self.appid,
            timeStamp=str(int(time.time())),
            nonceStr=gen_random_str(),
            package='prepay_id={0}'.format(prepay_id),
            signType='MD5',
        )
        data['paySign'] = self.get_sign(data)
        return data

    def check_sign(self, data):
        """检查微信支付回调签名是否正确"""
        if 'sign' not in data:
            return False
        tmp_data = data.copy()
        del tmp_data['sign']
        sign = self.get_sign(tmp_data)
        return data['sign'] == sign

    @staticmethod
    def notify_response(return_code='SUCCESS', return_msg='OK'):
        """通知结果的返回"""
        return dict_to_xml(return_code=return_code, return_msg=return_msg)

    def check_data(self, data, check_sign=True):
        """检查请求结果或者支付通知数据的正确性
        如果结果不合法会抛出一个WXPayError的子类

        :params data: xml转化成的dict数据
        :return: no return
        :raises ReturnCodeFail: return_code FAIL
        :raises ResultCodeFail: result_code FAIL
        :raises SignError: 签名错误

        例如处理支付回调用法::

            data = xml_to_dict(xml)
            try:
                wxpay.check_data(data)
            except SignError:
                return wxpay.notify_response('FAIL', '签名错误')
            except WXPayError:
                logger.error('微信支付数据错误', exc_info=True)
                return wxpay.notify_response('FAIL', '数据错误')

            do something handle trade
            ...

            return wxpay.notify_response()
        """
        if data['return_code'] == 'FAIL':
            raise ReturnCodeFail(data['return_msg'])
        elif data['result_code'] == 'FAIL':
            raise ResultCodeFail(data['err_code'], data['err_code_des'])
        elif check_sign and not self.check_sign(data):
            raise SignError()
