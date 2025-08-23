import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mysql.init_app(app)
    app.secret_key = app.config['SECRET_KEY']

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
