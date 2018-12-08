from flask import Flask

from .core import wx_oauth, wxpay
from .veiws import bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    wx_oauth.init_app(app)
    wxpay.init_app(app)

    app.register_blueprint(bp)

    return app
