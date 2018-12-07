from flask import Blueprint, redirect, render_template, request, session, url_for

from flask_wxpay import now_str, xml_to_dict
from .core import wx_oauth, wxpay

bp = Blueprint('views', __name__)


@bp.route('/')
def index():
    openid = session.get('openid')
    if not openid:
        # 授权获取openid
        authorized_url = wx_oauth.get_authorize_url(redirect_uri=url_for('.authorized', _external=True))
        return redirect(authorized_url)
    # 统一下单接口
    out_trade_no = now_str()
    ip = request.remote_addr
    total_fee = 101
    data = wxpay.unified_order(out_trade_no, total_fee, ip, '测试商品', 600, openid=openid)
    if data['return_code'] == 'SUCCESS':
        prepay_data = wxpay.get_jsapi_prepay_data(data['prepay_id'])
    else:
        prepay_data = ''
    return render_template('unified_order.html', total_fee=total_fee, prepay_data=prepay_data)


@bp.route('/authorized')
def authorized():
    code = request.args.get('code')
    if not code:
        return 'missing param code'

    access_token = wx_oauth.get_access_token(code)
    session['openid'] = access_token['openid']
    return redirect('http://wx.huimaofitness.com' + url_for('.index'))


@bp.route('/wxpay/notify', methods=['POST'])
def notify():
    xml = request.get_data()
    data = xml_to_dict(xml)
    print('notify data', data)
    resp = wxpay.notify_response()
    print('notify resp', resp)
    return resp


@bp.route('/hello')
def hello():
    return 'hello'
