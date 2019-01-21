from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
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
    total_fee = 1
    expire_seconds = 600
    data = wxpay.unified_order(out_trade_no, total_fee, ip, '测试商品', expire_seconds, openid=openid)
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
    return redirect(current_app.config['REDIRECT_HOST'] + url_for('.index'))


@bp.route('/wxpay/notify', methods=['POST'])
def notify():
    xml = request.get_data()
    data = xml_to_dict(xml)
    print('notify data', data)
    resp = wxpay.notify_response()
    print('notify resp', resp)
    return resp


@bp.route('/show-user-openid')
def show_user_openid():
    return session.get('openid')


@bp.route('/transfers')
def transfers():
    # 企业付款到零钱
    partner_trade_no = f'test{now_str()}'
    openid = current_app.config['YOUR_OPENID']
    amount = 30
    resp = wxpay.transfers(partner_trade_no, openid, amount, '描述', '127.0.0.1')
    print(resp)
    return partner_trade_no


@bp.route('/get-transfers-info')
def partner_trade_no():
    partner_trade_no = 'test20190108212028745982'
    transfers_info = wxpay.get_transfers_info(partner_trade_no)
    return jsonify(transfers_info)


@bp.route('/hello')
def hello():
    return 'hello'
