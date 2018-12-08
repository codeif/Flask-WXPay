微信支付Flask扩展
===================

文档
----

帮助文档: http://flask-wxpay.readthedocs.io/en/latest/


使用
----

initialized::

    from flask_wxpay import WXPay
    wxpay = WXPay()
    wxpay.init_app(app)

创建订单,生成prepay data::

    from flask_wxpay import now_str
    from core import wxpay

    out_trade_no = now_str()
    order_data = wxpay.unified_order(out_trade_no, total_fee, ip, body, openid=openid)
    prepay_data = wxpay.get_jsapi_prepay_data(order_data['prepay_id'])


配置项
------

==========================  =====================================================
WXPAY_BASE_URL              默认值: https://api.mch.weixin.qq.com
WXPAY_REQUEST_TIMEOUT       默认值: 10
WX_APPID                    公众账号ID
WXPAY_MCHID                 商户号
WXPAY_KEY                   商户支付密钥Key
WXPAY_NOTIFY_URL            默认异步通知url
WXPAY_ROOTCA_PATH           rootca证书路径，对应requests的verify参数,默认为None
WXPAY_APICLIENT_CERT_PATH   客户端证书路径，默认值None
WXPAY_APICLIENT_KEY_PATH    客户端证书key的路径，默认值None
WXPAY_SANDBOX               是否使用沙箱环境，默认为 False
==========================  =====================================================
