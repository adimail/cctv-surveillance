from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from app.extensions import db

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = "nqMt+o1BxO2Wkaj4ogmFtg=="
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    from app.blueprints.home import home_bp
    from app.blueprints.api import api
    from app.blueprints.feed import feed
    from app.blueprints.auth import auth
    from app.blueprints.history import history_bp
    from app.blueprints.broadcast import broadcast_bp
    from app.blueprints.analytics import analytics_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(feed, url_prefix='/feed')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(broadcast_bp, url_prefix='/broadcast')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')

    limiter.limit("200 per hour")(home_bp)
    limiter.limit("200 per hour")(api)
    limiter.limit("200 per hour")(feed)
    limiter.limit("200 per hour")(auth)
    limiter.limit("200 per hour")(history_bp)
    limiter.limit("200 per hour")(broadcast_bp)
    limiter.limit("200 per hour")(analytics_bp)

    @app.errorhandler(404)
    def page_not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html", message=str(error)), 500

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(400)
    def bad_request(_):
        return render_template("errors/400.html"), 400

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html", error=e.description), 400

    return app
