from flask import Flask, render_template
from app.blueprints.home import home_bp
from app.blueprints.api import api
from app.blueprints.feed import feed
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(feed, url_prefix='/feed')

    limiter.limit("200 per hour")(home_bp)
    limiter.limit("200 per hour")(api)
    limiter.limit("200 per hour")(feed)

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
