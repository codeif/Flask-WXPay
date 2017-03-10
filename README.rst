微信支付Flask扩展
================

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

    out_trade_no = wxpay.gen_out_trade_no()
    order_data = wxpay.unified_order(out_trade_no, price, ip, body, openid=openid)
    prepay_data = wxpay.get_jsapi_prepay_data(order_data['prepay_id'])


配置项
------

==========================  =============================
WX_APPID                    公众账号ID
WXPAY_MCHID                 商户号
WXPAY_KEY                   商户支付密钥Key
WXPAY_NOTIFY_URL            默认异步通知url
WXPAY_CERT_PATH             默认值None
WXPAY_CERT_KEY_PATH         默认值None
==========================  =============================
