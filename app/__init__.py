from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restful import Api

from config import Config
from app.utils import localize_comments, convert_image_to_base64

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
api = Api(app, prefix="/api")

app.jinja_env.globals["localize_comments"] = localize_comments
app.jinja_env.globals["convert_image_to_base64"] = convert_image_to_base64

from app import routes, models, errors
from .api import api as api_serivce
