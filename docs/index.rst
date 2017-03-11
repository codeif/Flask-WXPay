:orphan:

Flask-WXPay
=============

一个微信支付的Flask插件,
`微信支付API <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1>`_


Installation
------------
Install the module with one of the following commands::

    pip install Flask-WXPay

Usage
-----

initialized::

    from flask_wxpay import WXPay
    wxpay = WXPay()
    wxpay.init_app(app)

创建订单,生成prepay data::

    from flask_wxpay import now_str
    from core import wxpay

    out_trade_no = now_str()
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


API
---

.. module:: flask_wxpay

.. autoclass:: WXPay
    :inherited-members:

.. autofunction:: xml_to_dict

.. autofunction:: dict_to_xml

.. autofunction:: gen_random_str

.. autofunction:: md5

.. autofunction:: now_str


Exception Classes
-----------------

The following error classes exist in Flask-WXPay:

.. module:: flask_wxpay.exceptions

.. autoexception:: WXPayError

.. autoexception:: CertError

.. autoexception:: ReturnCodeFail

.. autoexception:: ResultCodeFail

.. autoexception:: SignError
