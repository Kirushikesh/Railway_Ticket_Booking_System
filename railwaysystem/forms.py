from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,DateField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Length
from datetime import datetime
#from flaskblog.models import User
import railwaysystem.models as fm
#from flask_login import current_user
class SearchTrains(FlaskForm):
    fromloc=StringField('From',validators=[DataRequired()])
    toloc=StringField('To',validators=[DataRequired()])
    Date=DateField('Date',format='%Y-%m-%d',
                        validators = [DataRequired('enter the date in the format yyyy-mm-dd')])
    submit=SubmitField('Search')

class RunningStatus(FlaskForm):
    trainname_trainno=StringField('Enter Train Name/Train No',validators=[DataRequired()])
    submit=SubmitField('Search')

class PnrStatus(FlaskForm):
    pnr_no=StringField('PNR NO',validators=[DataRequired(),Length(min=10,max=10)],render_kw={"placeholder": "Enter Your 10 digit pnr number"})
    submit=SubmitField('Search')

class Trains(FlaskForm):
    train=StringField('Train Name/Number',validators=[DataRequired()],render_kw={"placeholder": "Enter the train name or number"})
    submit=SubmitField('Search')

class Station(FlaskForm):
    station=StringField('Station Name/Code',validators=[DataRequired()],render_kw={"placeholder": "Enter the station name or code"})
    submit=SubmitField('Search')

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),
                                    Length(min=2,max=20)], render_kw={"placeholder": "enter the name here"})
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm_Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        user=fm.username_exist(username.data)
        if user:
            raise ValidationError('That User name is taken. Please choose an another')
    
    def validate_email(self,email):
        user=fm.email_exist(email.data)
        if user:
            raise ValidationError('That Email is taken. Please choose an another ')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember ME')
    submit=SubmitField('Log in')