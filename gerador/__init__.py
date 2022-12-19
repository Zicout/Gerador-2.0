from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config["SECRET_KEY"] = "ce5085d2b4ce7bd2f92094808f601e88"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça Login para Continuar"
login_manager.login_message_category = "alert-info"

from gerador import routes

