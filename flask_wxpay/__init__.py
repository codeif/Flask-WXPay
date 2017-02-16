# -*- coding: utf-8 -*-
"""微信支付的flask扩展"""
from datetime import datetime, timedelta
import time
import random
import json
import requests

import httpdns

from .utils import gen_random_str, md5, data_to_xml, xml_to_data
from .exceptions import WXPayError, WXPayCertError


class WXPay(object):

    def __init__(self, app=None):
        self.api_host = 'api.mch.weixin.qq.com'
        self.scheme = 'https'
        self.api_host_ip = httpdns.get_ip(self.api_host)
        self.timeout = 10

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.appid = app.config['WX_APPID']
        self.mch_id = app.config['WXPAY_MCHID']
        self.key = app.config['WXPAY_KEY']
        self.notify_url = app.config['WXPAY_NOTIFY_URL']

        self.cert_path = app.config.get('WXPAY_CERT_PATH')
        self.cert_key_path = app.config.get('WXPAY_CERT_KEY_PATH')

        self.out_trade_no_prefix = \
            app.config.get('WXPAY_OUT_TRADE_NO_PREFIX', 'wx')
        self.out_refund_no_prefix = \
            app.config.get('WXPAY_OUT_REFUND_NO_PREFIX', 'ref')

    def _post(self, path, params, cert=False):
        """添加发送签名
        处理返回结果成dict, 并检查签名
        """
        base_params = dict(
            appid=self.appid,
            mch_id=self.mch_id,
            nonce_str=gen_random_str()
        )
        if path == '/mmpaymkttransfers/sendredpack':
            del base_params['appid']
        params.update(base_params)

        params['sign'] = self.get_sign(params)

        xml_data = data_to_xml(params).encode('utf-8')
        if cert:
            if not (self.cert_path and self.cert_key_path):
                raise WXPayCertError()
            api_cert = (self.cert_path, self.cert_key_path)
        else:
            api_cert = None

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
        data = xml_to_data(xml)
        if not (cert or self.check_sign(data)):
            msg = u'path-{0} result sign error\n body-{1}'.format(path, xml)
            raise WXPayError(msg)
        return data

    @staticmethod
    def _gen_out_no(prefix):
        """用于生成随机单号的"""
        now_str = datetime.now().strftime('%Y%m%d%H%M%S%f')
        chars = 'abcdefghijklmnopqrstuvwxyz'
        return '{0}{1}{2}'.format(prefix, random.choice(chars), now_str)

    def gen_out_trade_no(self):
        """生成out_trade_no"""
        prefix = self.out_trade_no_prefix
        return self._gen_out_no(prefix)

    def gen_out_refund_no(self):
        """生成退款单号"""
        prefix = self.out_refund_no_prefix
        return self._gen_out_no(prefix)

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

    def unified_order(self, out_trade_no, total_fee, ip, body,
                      notify_url=None, trade_type='JSAPI', openid=None):
        """统一下单
        api: https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_1
        """
        api_path = '/pay/unifiedorder'
        now = datetime.now()
        time_start = now.strftime('%Y%m%d%H%M%S')
        time_expire = (now + timedelta(minutes=5, seconds=5))\
            .strftime('%Y%m%d%H%M%S')

        params = dict(
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
            params['openid'] = openid

        data = self._post(api_path, params)

        if data['return_code'] != 'SUCCESS':
            msg = '统一下单错误, msg-{0},\nparams-{1}' \
                .format(data['return_msg'], json.dumps(params))
            raise WXPayError(msg)

        return data

    def query_order(self, transaction_id=None, out_trade_no=None):
        """查询订单
        api: https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_2&index=4
        """
        api_path = '/pay/orderquery'
        if not (transaction_id or out_trade_no):
            raise WXPayError('查询订单需要transaction_id or out_trade_no')
        params = dict()
        if transaction_id:
            params['transaction_id'] = transaction_id
        else:
            params['out_trade_no'] = out_trade_no

        data = self._post(api_path, params)
        return data

    def close_order(self, out_trade_no):
        """关闭订单
        api:https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_3&index=5
        """
        api_path = '/pay/closeorder'
        params = dict(out_trade_no=out_trade_no)
        return self._post(api_path, params)

    def refund(self, out_trade_no, out_refund_no, total_fee, refund_fee):
        """退款
        api: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4
        """
        api_path = '/secapi/pay/refund'
        params = dict(
            out_trade_no=out_trade_no,
            out_refund_no=out_refund_no,
            total_fee=total_fee,
            refund_fee=refund_fee,
            op_user_id=self.mch_id
        )
        return self._post(api_path, params, cert=True)

    def gen_mch_billno(self):
        """商户订单号（每个订单号必须唯一）
        组成：mch_id+yyyymmdd+10位一天内不能重复的数字。
        接口根据商户订单号支持重入，如出现超时可再调用。
        """
        now_str = datetime.now().strftime('%Y%m%d%H%M%S%f')[:18]
        return '{0}{1}'.format(self.mch_id, now_str)

    def sendredpack(self, mch_billno, send_name, re_openid, total_amount,
                    wishing, client_ip, act_name, remark):
        """发红包
        :param mch_billno: 商户订单号
        :param send_name: 商户名称
        :param re_openid: 用户openid
        :param total_amount: 付款金额
        :param wishing: 红包祝福语
        :param client_ip: 调用接口的机器IP地址
        :param act_name: 活动名称
        :param remark: 备注信息
        """
        api_path = '/mmpaymkttransfers/sendredpack'
        params = dict(
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
        return self._post(api_path, params, cert=True, sendredpack=True)

    def get_redpack_info(self, mch_billno):
        """查询红包信息
        :param mch_billno: 商户订单号
        """
        api_path = '/mmpaymkttransfers/gethbinfo'
        params = dict(
            mch_billno=mch_billno,
            bill_type='MCHT'
        )
        return self._post(api_path, params, cert=True)

    def get_app_prepay_data(self, prepay_id):
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
