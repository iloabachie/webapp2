from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_wtf import FlaskForm 
from wtforms import StringField, IntegerField, DateField, SubmitField, PasswordField, EmailField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.exc import OperationalError 
from icecream import ic
import os
from datetime import datetime, date
import openai_model
from email_model import send_email
from loremipsum import get_paragraph
from hashlib import sha256
from werkzeug.security import generate_password_hash, check_password_hash

# ic(type(session), type(request))

app = Flask(__name__) 
app.config['SECRET_KEY'] = "mysecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Add Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 


# Initialize the database
db = SQLAlchemy(app)

# create a model
class Users(db.Model): # No need to define init class
    __tablename__ = "registered_users"
    user_id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)    
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return "<Name %r>" % self.fname + "|" + self.lname + "|" + self.username + "|" + self.email

# Create a function to create the database tables for sqllite
# def create_tables():
#     with app.app_context():        
#         db.create_all()

# Example: Run the create_tables function when the script is executed
# if __name__ == '__main__':
#     create_tables()
    
@app.context_processor
def inject_defaults():
    default_year = date.today()
    company_name = "Teddox"
    # glorem = get_paragraph(start_with_lorem=True)
    return dict(default_year=default_year, company_name=company_name) #, lorem=glorem)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def home():
    return render_template("welcome.html")

password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{10,}$"
class SignUpForm(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired()])
    lname = StringField("Last Name", validators=[DataRequired()])
    username = StringField("username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    # password1 = PasswordField("Password", validators=[Regexp(regex=password_regex, message="password requirement not met")])
    # password2 = PasswordField("Retype password", validators=[Regexp(regex=password_regex, message="password requirement not met")])
    password1 = PasswordField("Password", validators=[DataRequired(), EqualTo(fieldname='password2', message="Password should match" )])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Create Account")


@app.route('/register', methods=['POST', "GET"])
def register():
    lorem = get_paragraph(start_with_lorem=True)
    form = SignUpForm()
    print('	\033[31mi got here1	\033[0m')
    if request.method == "POST":
        if form.validate_on_submit():
            email_taken = False
            user_taken = False
            no_match = False
            fname = form.fname.data            
            lname = form.lname.data
            username = form.username.data
            email = form.email.data            
            user_e = Users.query.filter_by(email=email).first()
            user_n = Users.query.filter_by(username=username).first()
            print('	\033[31mi got here2	\033[0m')
            password1 = form.password1.data  
            password2 = form.password2.data 
            if password1 != password2:
                no_match = True
            if user_e:
                email_taken = True
            if user_n:
                user_taken = True
            if user_e or user_n or no_match:
                return render_template("register.html", lorem=lorem, form=form, email_taken=email_taken, user_taken=user_taken, no_match=no_match)
                        
            # print(password1, password2)
            # print('	\033[31mi got here3	\033[0m')
            # password_hash = sha256(password2.encode()).hexdigest()
            # print(111, password_hash, print(len(password_hash)))
            hashed_pw = generate_password_hash(password1, 'pbkdf2')
            user = Users(fname=fname, lname=lname, username=username, email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Profile created successfully")  # lets see if it works
            # Clear Form fileds pending
            print('	\033[31mi got here4	\033[0m')
            userlist = Users.query.order_by(Users.date_added)  
            return render_template('loggedin.html', fname=fname, userlist=userlist)            
        
    return render_template("register.html", lorem=lorem, form=form)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    # ic(type(form.password1.label(class="form-label")))
    if request.method == 'POST':        
        if form.validate_on_submit():
            username = form.username.data
            form.username.data = None
            password = form.password.data  
            form.password.data = None
            # authentication logic
            ic(username, password)
            return render_template('loggedin.html', user=username)
    return render_template("login_page.html", form=form)

@app.route("/process", methods=['POST', 'GET'])
def process():
    print("process1 running")
    result = None
    if request.method == 'POST':
        if not result:
            name = request.form.get('patients_name')    
            address = request.form.get('patients_address')
            query = request.form.get('query')     
            completion = openai_model.gpt35model(query) 
            completion = completion.split('\n')
            result = [name, address, query, completion] 
            session["ai_output"] = result
            flash(f"Processed information... for {name}") # added to aioutput but not working.
            return render_template('ai_output.html', pname=name, result=result) 
    return render_template("ai_req_form.html")

# changing form to WTF
# ====================================
class AiInputForm(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired()])
    mname = StringField("Middle Name", validators=[DataRequired()])
    lname = StringField("Last Name", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    dob = DateField("DOB", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    message1 = StringField("Information1", validators=[DataRequired()])
    message2 = StringField("Information2", validators=[DataRequired()])
    message3 = StringField("Information3", validators=[DataRequired()])
    message4 = StringField("Information4", validators=[DataRequired()])
    message5 = StringField("Information5", validators=[DataRequired()])
    submit = SubmitField("Process")
    
@app.route("/process2", methods=['POST', 'GET'])
def process2():
    print('process2 running')
    form = AiInputForm()
    result = None
    if request.method == 'POST':
        if form.validate_on_submit():
            fname = form.fname.data            
            mname = form.mname.data
            lname = form.lname.data
            age = form.age.data
            dob = form.dob.data
            location = form.location.data
            message1 = form.message1.data
            message2 = form.message2.data
            message3 = form.message3.data
            message4 = form.message4.data
            message5 = form.message5.data
            info = [message1, message2, message3, message4, message5]
            completion = openai_model.gpt35model(' '.join(info)) 
            completion = completion.split('\n')
            result = [fname, mname, lname, age, dob, location, completion] 
            session["ai_output"] = result
            flash(f"Processed information... for {fname} {lname}") # added to aioutput but not working.
            return render_template('ai_output.html', pname=fname, result=result) 
    return render_template("ai_req_form2.html", form=form)
#=======================================

# @app.route('/loggedin')
# def welcome():
#     return render_template('loggedin.html')     

@app.route('/send_mail', methods=['POST', 'GET'])
def send_to_email():  
    if request.method == "GET":
        result = session.get('ai_output')
        subject = result[0] + '-' + result[2]
        completion = '\n'.join(result[-1])
        body = f"{result[3]} \n{completion}"
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
    # app.run(host='0.0.0.0', port=5000, debug=True) # for dev testing
    app.run() # For production