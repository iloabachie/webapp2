from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy 
from icecream import ic
import os
import datetime
import openai_model
from email_model import send_email

ic(type(session), type(request))

app = Flask(__name__) 
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Add Database


# Initialize the database
db = SQLAlchemy(app)

# create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = True # used in tracking active accounts
    
    def __repr__(self):
        return "<Name %r>" % self.name
    

# Not used yet
class PatientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    query = StringField("Query", validators=[DataRequired()])
    submit = SubmitField("Submit")
# -----------------------------
    
    
@app.context_processor
def inject_defaults():
    default_year = datetime.date.today()
    company_name = "Teddox"
    return dict(default_year=default_year, company_name=company_name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def home():
    return render_template("welcome.html")


@app.route('/register', methods=['POST', "GET"])
def register():
    return render_template("register.html")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data  
            # authentication logic
            ic(username, password)
            return render_template('loggedin.html', user=username)
    return render_template("login_page.html", form=form)

@app.route("/process", methods=['POST', 'GET'])
def process():
    result = None
    if request.method == 'POST':
        if not result:
            pname = request.form.get('patients_name')    
            paddress = request.form.get('patients_address')
            pquery = request.form.get('query')     
            completion = openai_model.gpt35model(pquery) 
            completion = completion.split('\n')
            result = [pname, paddress, pquery, completion] 
            session["ai_output"] = result
            return render_template('ai_output.html', result=result) 
        else:
            pass
    return render_template("ai_req_form.html")

@app.route('/loggedin')
def welcome():
    return render_template('loggedin.html')
     

@app.route('/send_mail', methods=['POST', 'GET'])
def send_to_email():  
    if request.method == "GET":
        result = session.get('ai_output')
        subject = result[0] + '-' + result[1]
        completion = '\n'.join(result[3])
        body = f"{result[2]} \n{completion}"
        ic(subject, body)    
        return render_template('emailform.html', subject=subject, body=body)
    if request.method == "POST":
        email = request.form.get('receiver')    
        subject = request.form.get('subject')
        message = request.form.get('message')
        ic(email, subject, message)
        is_sent = send_email(email, subject, message)
        if is_sent:
            return render_template('emailsent.html', email=email)
        else:
            return render_template('emailfail.html', email=email)

# used to redirect
@app.route('/test')
def source_route():
    import time
    time.sleep(5)
    return redirect(url_for('process'))

@app.route('/logout')
def logout():
    #add log out code
    return render_template("loggedout.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)