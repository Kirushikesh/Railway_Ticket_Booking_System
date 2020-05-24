from flask import render_template,url_for,flash,redirect,request,jsonify,make_response
from railwaysystem.models import User
from railwaysystem.forms import SearchTrains,RunningStatus,PnrStatus,Trains,Station,RegistrationForm,LoginForm
from railwaysystem import app,mysql,bcrypt
import railwaysystem.models as fm
from flask_login import login_user,current_user,logout_user,login_required
import railwaysystem.train.ex as tt
from datetime import datetime
aglobal={}

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
        return redirect(url_for('train_details',train=form.train.data))
    return render_template('trains.html',form=form)

@app.route("/train/<string:train>")
def train_details(train):
    train,station,default=fm.detail_particular_train(train)
    return render_template('particular_train.html',train=train,station=station,default=default)

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

@app.route("/giveawayseats",methods=['POST'])
def give():
    req=request.get_json()
    arr=tt.seat_availability(req['train_no'],req['t_class'],req['from'],req['to'])
    out=[]
    for i in range(len(arr)):
        flag=[]
        if(arr[i]=='NaN'):
            noofwl=fm.no_of_wl(req['train_no'],req['date'][i],req['from'],req['to'],req['t_class'])
            flag.append('Waiting List: ')
            flag.append('tomato')
            flag.append(noofwl)
        elif(arr[i]>0):
            flag.append('Available: ')
            flag.append('lightgreen')
            flag.append(arr[i])
        else:
            flag.append('RAC: ')
            flag.append('darkorange')
            flag.append(-1*arr[i])
        out.append(flag)
    res=make_response(jsonify(out),200)
    return res

@app.route("/bookpassenger",methods=['GET','POST'])
@login_required
def book():
    global aglobal
    aglobal=request.args
    return render_template('passengerdetails.html',form=aglobal)

@app.route("/passengers",methods=['POST'])
def final_book():
    global aglobal
    if(request.method=='POST'):
        out=[]
        data=request.form
        noofpass=int(data['noofpass'])
        day=fm.return_full_day(aglobal['day'])
        fro_stopno,to_stopno=fm.return_stop_no(aglobal['no'],aglobal['from'],aglobal['to'])
        from_ind=1
        to_ind=1

        while(noofpass>0):
            vac_common=tt.seat_availability_onthatday(int(aglobal['no']),day,aglobal['t_class'],fro_stopno,to_stopno)
            if(vac_common=='NaN'):
                print('NAN')
                from_ind=to_ind
                to_ind=from_ind+noofpass
                out1=fm.book_wl(data,aglobal,noofpass,from_ind,to_ind)
                noofpass=0
                out.append(out1)

            elif(vac_common>0):
                from_ind=1
                #print(from_ind,vac_common,noofpass)
                if(vac_common>=noofpass):
                    to_ind=noofpass+1
                    out1=fm.book_train_fm(data,aglobal,aglobal['t_class'],noofpass,from_ind,to_ind)
                    noofpass=0
                else:
                    to_ind=vac_common+1
                    out1=fm.book_train_fm(data,aglobal,aglobal['t_class'],vac_common,from_ind,to_ind)
                    noofpass-=vac_common
                
                status_no=1
                out.append(out1)

            elif(vac_common<0):
                from_ind=to_ind
                #print(from_ind,to_ind,vac_common,noofpass)
                if((-1*vac_common)>=noofpass):
                    to_ind=from_ind+noofpass
                    out1=fm.book_train_fm(data,aglobal,aglobal['t_class']+'_R',noofpass,from_ind,to_ind)
                    noofpass=0
                else:
                    to_ind=from_ind+(-1*vac_common)
                    out1=fm.book_train_fm(data,aglobal,aglobal['t_class']+'_R',(-1*vac_common),from_ind,to_ind)
                    noofpass-=(-1*vac_common)
                
                status_no=1
                out.append(out1)
    #print(out,aglobal,data)
    return render_template('displayticket.html',form=out,train_details=aglobal,passengers=data)
