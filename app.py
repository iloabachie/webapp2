from flask import Flask, render_template, request, flash
# from flask_wtf import FlaskForm # py -m pip install flask-wtf 
# from wtforms import StringField, SubmitField, PasswordField
# from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy #py -m pip install flask-sqlalchemy
import os
import datetime
# import openai_model
from email_model import send_email

if __name__ == "__main__":
    app = Flask(__name__) 

@app.context_processor
def inject_defaults():
    default_year = datetime.date.today()
    company_name = "Teddox"
    return dict(default_year=default_year, company_name=company_name)

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def server_error(e):
#     return render_template('500.html'), 500

@app.route('/')
def home():
    return render_template("welcome.html")


@app.route('/register', methods=['POST', "GET"])
def register():
    return render_template("register.html")


@app.route('/login')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)