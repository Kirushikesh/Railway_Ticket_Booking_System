from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,DateField,IntegerField,RadioField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Length
from datetime import datetime
from railwaysystem.models import User
import railwaysystem.models as fm
from flask_login import current_user
from railwaysystem import mysql

class SearchTrains(FlaskForm):
    fromloc=StringField('From',validators=[DataRequired()])
    toloc=StringField('To',validators=[DataRequired()])
    Date=DateField('Date',format='%Y-%m-%d',
                        validators = [DataRequired('enter the date in the format yyyy-mm-dd')])
    submit=SubmitField('Search')

    def validate_fromloc(self,fromloc):
        cur=mysql.connection.cursor()
        cur.execute("select * from station where station_name=%s",(fromloc.data,))
        flag=cur.fetchone()
        if not flag:
            raise ValidationError('there seems to be no matching station.why dont u try a different spelling?')
    def validate_toloc(self,toloc):
        cur=mysql.connection.cursor()
        cur.execute("select * from station where station_name=%s",(toloc.data,))
        flag=cur.fetchone()
        if not flag:
            raise ValidationError('there seems to be no matching station.why dont u try a different spelling?')
 
class PnrStatus(FlaskForm):
    pnr_no=StringField('PNR NO',validators=[DataRequired(),Length(min=10,max=10)],render_kw={"placeholder": "Enter Your 10 digit pnr number"})
    submit=SubmitField('Search')

    def validate_pnr_no(self,pnr_no):
        cur=mysql.connection.cursor()
        cur.execute("select * from passenger where pnr=%s",(pnr_no.data,))
        flag=cur.fetchone()
        if not flag:
            raise ValidationError('No such pnr no exist')
class Trains(FlaskForm):
    train=StringField('Train Name/Number',validators=[DataRequired()],render_kw={"placeholder": "Enter the train name or number"})
    submit=SubmitField('Search')
    def validate_train(self,train):
        cur=mysql.connection.cursor()
        try:
            tno=int(train.data)
            flag=cur.execute("select * from train where train_no=%s",(tno,))
            if not flag:
                raise ValidationError('No such Train Name or Number exist')
        except:
            flag=cur.execute("select * from train where train_name=%s",(train.data,))
            if not flag:
                raise ValidationError('No such Train Name or Number exist')

class Station(FlaskForm):
    station=StringField('Station Name/Code',validators=[DataRequired()],render_kw={"placeholder": "Enter the station name or code"})
    submit=SubmitField('Search')
    def validate_station(self,station):
        cur=mysql.connection.cursor()
        try:
            tno=int(station.data)
            flag=cur.execute("select * from station where station_no=%s",(tno,))
            if not flag:
                raise ValidationError('No such station Name or Number exist')
        except:
            flag=cur.execute("select * from station where station_name=%s",(station.data,))
            if not flag:
                raise ValidationError('No such station Name or Number exist')

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),
                                    Length(min=2,max=20)], render_kw={"placeholder": "enter the name here"})
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('confirm_Password',validators=[DataRequired(),EqualTo('password')])
    gender=RadioField('Gender',choices = [('M','Male'), ('F','Female')],default='M')
    age=IntegerField('Age',validators=[DataRequired()])
    city=StringField('City',validators=[DataRequired()])
    state=StringField('State',validators=[DataRequired()])
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

class Passenger_details(FlaskForm):
    p_name=StringField('Passenger Name',validators=[DataRequired(),
                                    Length(min=2,max=20)], render_kw={"placeholder": "enter the name here"})
    age=IntegerField('Age',validators=[DataRequired()])
    gender=RadioField('Gender',choices = [('M','Male'), ('F','Female')],default='M')
    submit=SubmitField('Book')