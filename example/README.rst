
`支付验收指引 <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=23_1>`_

`微信支付开发步骤 <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_3>`_

`微信网页授权 <https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842>`_


配置文件instance/config.py内容

.. code-block:: py

    SECRET_KEY = b'z\x90\x13\x95\xb0\xe6]\xcfdB'

    WX_APPID = 'your wx appid'
    WX_SECRET = 'your wx secret'

    WXPAY_MCHID = '商户号'
    WXPAY_KEY = 'your wxpay key'
    WXPAY_NOTIFY_URL = 'your pay notify url'

    # WXPAY_SANDBOX = True

    WXPAY_APICLIENT_CERT_PATH = '/app/example/instance/apiclient_cert.pem'
    WXPAY_APICLIENT_KEY_PATH = '/app/example/instance/apiclient_key.pem'

    YOUR_OPENID = 'your open id'
    REDIRECT_HOST = 'http://youdomain.com'



配置
---------

1. 公众号后台 开发 -> 接口权限 -> 网页授权获取用户基本信息 -> 修改 -> 网页授权域名配置获取openid的域名
2. 微信支付后台 -> 产品中心 -> 开发配置 -> 支付授权目录 配置支付页面的目录

运行示例代码
--------------

.. code-block:: sh

    docker build -t flask-wxpay .
    docker run -p 5000:5000 flask-wxpay

补充
-----

沙箱环境可以支付 1.01 元的， 提示 缺少参数 total_fee 是正常的，只要回调正常就说明是正常的