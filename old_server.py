from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm # py -m pip install flask-wtf 
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy #py -m pip install flask-sqlalchemy
import os
import datetime
import openai_model
from email_model import send_email
import ConsolePrint

app = Flask(__name__)  # Create a flask Instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Add Database
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

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

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Not used yet
class PatientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    query = StringField("Query", validators=[DataRequired()])
    submit = SubmitField("Submit")
# -----------------------------

@app.context_processor
def inject_defaults():
    default_year = datetime.date.today().year
    company_name = "Teddox"
    return dict(default_year=default_year, company_name=company_name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route("/")
def home():
    return render_template("welcome_index.html")

logged_in = False
new_completion = True
@app.route("/login", methods=['POST', 'GET'])
def login():
    global new_completion, logged_in
    if not logged_in:          
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data  
        
            if username in ["userone", "usertwo"] and password in ["password#", "password$"]: 
                logged_in = True 
                return render_template("index.html")
            else:
                return render_template("invalid.html", username=username)
    
        return render_template("login.html", form=form)
    new_completion = True       
    return render_template("index.html")



@app.route('/process', methods=['POST', "GET"])
def process():
    global new_completion, completion, emailbody
    print(request.form, type(request.form))
    pname = request.form.get('patients_name')    
    paddress = request.form.get('patients_address')
    pquery = request.form.get('query')     
    if new_completion:        
        completion = openai_model.gpt35model(pquery) 
        completion = completion.split("\n")
        new_completion = False   
    emailbody = [pname, paddress, pquery, completion]   
    
    # ConsolePrint.startConsoleSave(name=r"textlogs\completions.txt")
    # print(completion, "\n===================\n")      
    # ConsolePrint.endConsoleSave(prompt=False)     
    return render_template("output.html", pname=pname, paddress=paddress, pquery=pquery, completion=completion)


@app.route('/messageform', methods=['POST', "GET"])
def messageform():    
    global sendtoemail
    sendtoemail = True
    pname, paddress, pquery, completion = emailbody  
    subject = pname + " - " + paddress
    completion = pquery + '\n' + '\n'.join(completion)  

    return render_template('messageform.html', subject=subject, pquery=pquery, completion=completion)

@app.route('/sent', methods=['POST', "GET"])
def mailsent():
    global sendtoemail
    if sendtoemail:
        email = request.form.get('receiver')    
        subject = request.form.get('subject')
        message = request.form.get('message')
        print(email, subject, message)
        
        if send_email(email, subject, message):
            sendtoemail = False
            return render_template("emailsent.html", email=email)        
        return render_template("emailfail.html", email=email)
    return "<h1> Not authorised </h1>"

@app.route('/loggedout')  
def log_out():
    global logged_in, new_completion
    logged_in = False
    new_completion = True
    return render_template("loggedout.html")

if __name__ == "__main__":
    app.run(debug=True)
