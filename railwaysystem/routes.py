from flask import render_template,url_for,flash,redirect,request
from railwaysystem.models import User
from railwaysystem.forms import SearchTrains,RunningStatus,PnrStatus,Trains,Station,RegistrationForm,LoginForm
from railwaysystem import app,mysql,bcrypt
import railwaysystem.models as fm
from flask_login import login_user,current_user,logout_user,login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/searchtrain",methods=['GET','POST'])
def searchtrain():
    form=SearchTrains()
    if form.validate_on_submit():
        output=fm.return_all_trains(form.fromloc.data,form.toloc.data,form.Date.data)
        return render_template('result_trains.html',form=output)
    return render_template('searchtrain.html',title='About',form=form)

@app.route("/runningstatus",methods=['GET','POST'])
def runningstatus():
    form=RunningStatus()
    if form.validate_on_submit():
        flash(f'Valid thing','success')
        return redirect(url_for('home'))
    return render_template('runningstatus.html',form=form)

@app.route("/pnrcheck",methods=['GET','POST'])
def pnrstatus():
    form=PnrStatus()
    if form.validate_on_submit():
        flash(f'Valid thing','success')
        return redirect(url_for('home'))
    return render_template('pnrcheck.html',form=form)

@app.route("/trains",methods=['GET','POST'])
def checktrains():
    form=Trains()
    if form.validate_on_submit():
        train,station=fm.detail_particular_train(form.train.data)
        return render_template('particular_train.html',train=train,station=station)
    return render_template('trains.html',form=form)

@app.route("/searchstation",methods=['GET','POST'])
def searchstation():
    form=Station()
    if form.validate_on_submit():
        return redirect(url_for('station_details',station=form.station.data))
    return render_template('searchstation.html',form=form)

@app.route("/station/<string:station>")
def station_details(station):
    station,id=fm.get_station_name(station)
    output=fm.search_station(id,station)
    return render_template('station.html',station_name=station,details=output)


@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        print('Valid Data')
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        fm.add_user(form.username.data,form.email.data,hashed_password,form.age.data,
                        form.gender.data,form.city.data,form.state.data)
        mysql.connection.commit()
        flash(f'Your Account has been created!You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Login',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=fm.email_exist(form.email.data)
        if user and bcrypt.check_password_hash(user['password'],form.password.data):
            Us=User(user)
            login_user(Us,remember=form.remember.data)
            flash('Login Successful.','success')
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:    
            flash('Login Unsuccessful.Please check the email or password','danger')
    return render_template('login.html',title='Login',form=form)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
