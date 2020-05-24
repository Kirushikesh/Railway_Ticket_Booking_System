from railwaysystem import mysql,login_manager
import calendar
from flask_login import UserMixin,current_user
import json
from datetime import datetime
from random import randint
import railwaysystem.train.ex as tex

@login_manager.user_loader
def load_user(user_id):
    cur=mysql.connection.cursor()
    cur.execute("select * from user WHERE email_id = %s ",(user_id,))
    Us=User(cur.fetchone())
    return Us

class User(UserMixin):
    def __init__(self,dictionary):
        self.email_id=dictionary['email_id']
        self.user_name=dictionary['user_name']
        self.password=dictionary['password']
        self.gender=dictionary['gender']
        self.age=dictionary['age']
        self.city=dictionary['city']
        self.state=dictionary['state']
    
    def get_id(self):
        return self.email_id

    def update_record(self,name,mail):
        self.username=name
        self.email=mail
        cur=mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s , email = %s WHERE id = %s",(self.username,self.email,self.id,))

def convert_no_name(from_loc,to_loc):
    cur=mysql.connection.cursor()
    cur.execute("select station_id from station where station_name = %s",(from_loc,))
    fro=cur.fetchone()
    fro=fro['station_id']
    cur.execute("select station_id from station where station_name = %s",(to_loc,))
    to=cur.fetchone()
    to=to['station_id']
    return (fro,to)

def return_train_class(no):
    cur=mysql.connection.cursor()
    cur.execute("""SELECT fare_1A,fare_2A,fare_3A,fare_SL from train_class where train_no=%s""",(no,))
    flag=cur.fetchone()
    hell=[]
    out=[]
    if( flag['fare_1A'] > 0 ):
        out.append('1A')
        hell.append(flag['fare_1A'])
    if( flag['fare_2A'] > 0 ):
        out.append('2A')
        hell.append(flag['fare_2A'])
    if( flag['fare_3A'] > 0 ):
        out.append('3A')
        hell.append(flag['fare_3A'])
    if( flag['fare_SL'] > 0 ):
        out.append('SL')
        hell.append(flag['fare_SL'])
    out.append(hell)

    return out

def convert_no_week(no):
    out=[]
    for i in list(no):
        if(i=='1'):
            out.append('Su')
        elif(i=='2'):
            out.append('Mo')
        elif(i=='3'):
            out.append('Tu')
        elif(i=='4'):
            out.append('We')
        elif(i=='5'):
            out.append('Th')
        elif(i=='6'):
            out.append('Fr')
        else:
            out.append('Sa')
    return out
    
def return_all_trains(from_loc,to_loc,date):
    cur=mysql.connection.cursor()
    date=date.isoweekday()
    date=date+1
    if(date==8):
        date=1
    from_loc,to_loc=convert_no_name(from_loc,to_loc)
    cur.execute("""select * from train_days where (available_days like '%%%s%%' and 
                    train_no in (select source.train_no from route_has_station as source JOIN route_has_station as destination on 
                        source.train_no=destination.train_no where (source.station_id= %s and destination.station_id= %s and 
                            source.stop_no < destination.stop_no)))""",(date,from_loc,to_loc,))
    information=[]
    flag=cur.fetchall()
    
    for i in flag:

        cur.execute("select * from train where train_no = %s",(i['train_no'],))
        temp=cur.fetchone()
        temp['available_days']=convert_no_week(i['available_days'])

        cur.execute("""select destination.source_distance-source.source_distance as distance,source.arrival_time as at,destination.arrival_time as dt 
                    from route as source join route as destination on source.train_no=destination.train_no where (
                    source.stop_no=(select stop_no from route_has_station where train_no= %s and station_id=%s) and 
                    destination.stop_no=(select stop_no from route_has_station where train_no= %s and station_id=%s) and 
                    source.train_no=%s
                    )""",(temp['train_no'],from_loc,temp['train_no'],to_loc,temp['train_no']))
        
        temp1=cur.fetchone()
        temp['distance']=temp1['distance']
        temp['source_time']=temp1['at']
        temp['destination_time']=temp1['dt']
        temp['available_class']=return_train_class(i['train_no'])
        temp['default_value']=temp['distance']*temp['available_class'][-1][0]
        information.append(temp)

    return information

def searchby_name_no(name_no):
    cur=mysql.connection.cursor()
    try:
        train_no=int(name_no)
        return train_no
    except:
        train_name=name_no
        flag=cur.execute("select train_no from train where train_name = %s",(train_name,))
        return cur.fetchone()['train_no']

def get_station_name(something):
    cur=mysql.connection.cursor()
    try:
        id=int(something)
        flag=cur.execute("select station_name from station where station_id = %s",(id,))
        if(flag):
            return (cur.fetchone()['station_name'],id)
        else:
            False
    except:
        flag=cur.execute("select station_id from station where station_name = %s",(something,))
        if(flag):
            return (something,cur.fetchone()['station_id'])
        else:
            False

def search_station(id,station_name):
    cur=mysql.connection.cursor()
    cur.execute("select train_no from route_has_station where station_id=%s",(id,))
    nos=cur.fetchall()
    information=[]
    for i in nos:
        cur.execute("select train_no,train_name,source_id,destination_id from train where train_no = %s",(i['train_no'],))
        temp=cur.fetchone()
        
        cur.execute("""SELECT r.arrival_time,r.departure_time FROM route as r join route_has_station 
            as rs on rs.train_no=r.train_no and rs.stop_no=r.stop_no where r.train_no=%s and rs.station_id=%s""",(temp['train_no'],id,))
        temp1=cur.fetchone()
        
        temp['arrival_time']=temp1['arrival_time']
        temp['departure_time']=temp1['departure_time']
        temp['stop_time']=temp1['departure_time']-temp1['arrival_time']
        
        cur.execute("select station_name from station where station_id = %s",(temp['source_id'],))
        temp['source_name']=cur.fetchone()['station_name']

        cur.execute("select station_name from station where station_id = %s",(temp['destination_id'],))
        temp['destination_name']=cur.fetchone()['station_name']
        
        del temp['source_id'],temp['destination_id']

        if(temp['arrival_time']==temp['departure_time'] and temp['source_name']==station_name):
            temp['arrival_time']='starts'
        elif(temp['arrival_time']==temp['departure_time'] and temp['destination_name']==station_name):
            temp['departure_time']='ends'
        
        information.append(temp)
    
    return information

def add_user(name,email,password,age,gender,city,state):
    cur=mysql.connection.cursor()
    cur.execute("""insert into user(user_name,email_id,password,age,gender,city,state) values(%s,%s,%s,%s,%s,%s,%s)""",(name,email,password,age,gender,city,state,))

def username_exist(uname):
    cur=mysql.connection.cursor()
    cur.execute("select * from user WHERE user_name = %s ",(uname,))
    return cur.fetchone()

def email_exist(mail):
    cur=mysql.connection.cursor()
    cur.execute("""select * from user where email_id = %s """,(mail,))
    return cur.fetchone()

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def detail_particular_train(something):
    trainno=searchby_name_no(something)
    cur=mysql.connection.cursor()
    cur.execute("""select * from train where train_no = %s """,(trainno,))
    information=cur.fetchone()
    cur.execute("""select available_days from train_days where train_no = %s """,(trainno,))
    information['available_days']=convert_no_week(cur.fetchone()['available_days'])

    cur.execute("""select source.arrival_time as at,destination.arrival_time as dt from route as source join route as destination 
                    on source.train_no=destination.train_no where (source.stop_no=(select stop_no from route_has_station where 
                    train_no= %s and station_id=%s) and destination.stop_no=(select stop_no from route_has_station where 
                    train_no= %s and station_id=%s) and source.train_no=%s)""",(information['train_no'],information['source_id']
                ,information['train_no'],information['destination_id'],information['train_no']))
    flag=cur.fetchone()
    information['source_time']=flag['at']
    information['destination_time']=flag['dt']
    cur.execute("""select s.station_name,rs.station_id,r.source_distance,r.arrival_time,r.departure_time,r.stop_no
                    from route_has_station as rs join route as r on r.train_no=rs.train_no and rs.stop_no=r.stop_no join station as s on 
                    rs.station_id=s.station_id where r.train_no=%s""",(information['train_no'],))
    station_details=cur.fetchall()
    for i in station_details:
        i['stop_time']=str(i['departure_time']-i['arrival_time'])
        if(i['arrival_time']==i['departure_time'] and i['station_id']==information['source_id']):
            i['arrival_time']='starts'
        elif(i['arrival_time']==i['departure_time'] and i['station_id']==information['destination_id']):
            i['departure_time']='ends'
        i['arrival_time']=str(i['arrival_time'])
        i['departure_time']=str(i['departure_time'])
    information['available_class']=return_train_class(trainno)
    
    cur.execute("select on_date from train_status where train_no=%s",(information['train_no'],))
    flag=cur.fetchall()
    information['days']=[]
    
    for i in flag:
        information['days'].append(i['on_date'])
    
    default=[]
    for i in information['available_class'][-1]:
        default.append(station_details[-1]['source_distance']*i)
    return (information,station_details,default)

def generate_pnr():
    cur=mysql.connection.cursor()
    while(1):
        randno=randint(10**9,(10**10)-1)
        flag=cur.execute("select * from passenger where pnr=%s",(randno,))
        if(flag>0):
            continue
        else:
            return randno

def return_full_day(day):
    if(day=='Su'):
        return 'Sunday'
    elif(day=='Mo'):
        return 'Monday' 
    elif(day=='Tu'):
        return 'Tuesday' 
    elif(day=='We'):
        return 'Wednesday' 
    elif(day=='Th'):
        return 'Thursday'
    elif(day=='Fr'):
        return 'Friday' 
    else:
        return 'Saturday'

def book_train_fm(passenger_dict,train_dict,book_class,noofpass,fromind,toind):
    cur=mysql.connection.cursor()
    information={}
    information['pnr_no']=[]

    cur.execute("select rs.stop_no,s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(train_dict['no'],train_dict['from'],))
    flag=cur.fetchone()
    fro_id=flag['station_id']
    fro=flag['stop_no']

    cur.execute("select rs.stop_no,s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(train_dict['no'],train_dict['to'],))
    flag=cur.fetchone()
    to_id=flag['station_id']
    to=flag['stop_no']

    information['seatno']=tex.book_train(train_dict['no'],return_full_day(train_dict['day']),book_class,fro,to,noofpass)
    cur.execute("select available_days from train_days where train_no=%s",(train_dict['no'],))
    information['available_days']=cur.fetchone()['available_days']

    flag=0
    for i in range(fromind,toind):
        age=str(i)+'age'
        name=str(i)+'name'
        gen=str(i)+'gender'
        pnr=generate_pnr()
        information['pnr_no'].append(pnr)
        cur.execute("insert into passenger values(%s,%s,%s,%s,%s)",(pnr,information['seatno'][flag],passenger_dict[name],passenger_dict[age],passenger_dict[gen],))
        mysql.connection.commit()
        cur.execute("insert into passenger_ticket values(%s,%s,%s,%s,%s)",(pnr,book_class,train_dict['rate'],fro_id,to_id,))
        mysql.connection.commit()
        date=datetime.strptime(train_dict['date'][:-3],"%a, %d %b %Y %H:%M:%S ")

        if(book_class[-2:]!='_R'):
            cur.execute("insert into reservation values(%s,%s,%s,%s,%s,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"CNF",date,))
        else:
            cur.execute("insert into reservation values(%s,%s,%s,%s,%s,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"RAC",date,))
        mysql.connection.commit()

        flag+=1
    return information

def return_stop_no(trainno,fro,to):
    cur=mysql.connection.cursor()
    cur.execute("select rs.stop_no from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(trainno,fro,))
    fro_s=cur.fetchone()['stop_no']
    cur.execute("select rs.stop_no from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(trainno,to,))
    to_s=cur.fetchone()['stop_no']
    return (fro_s,to_s)

def no_of_wl(trainno,day,fro,to,t_class):
    cur=mysql.connection.cursor()
    cur.execute("select s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where train_no=%s and rs.stop_no=%s",(trainno,fro,))
    fro=cur.fetchone()['station_id']
    cur.execute("select s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where train_no=%s and rs.stop_no=%s",(trainno,to,))
    to=cur.fetchone()['station_id']
    day=datetime.strptime(day[:-3],"%a, %d %b %Y %H:%M:%S ")
    flag=cur.execute("""select * from reservation as r join passenger_ticket as pt on r.pnr=pt.pnr where 
                (r.reservation_status="WL" and r.train_no=%s and r.reservation_date=%s and pt.class_type=%s and
                     pt.source_id=%s and pt.destination_id=%s)""",(trainno,day,t_class,fro,to,))
    return flag

def book_wl(passenger_dict,train_dict,noofpass,fromind,toind):
    cur=mysql.connection.cursor()
    information={}
    information['pnr_no']=[]

    cur.execute("select rs.stop_no,s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(train_dict['no'],train_dict['from'],))
    flag=cur.fetchone()
    fro_id=flag['station_id']
    fro=flag['stop_no']

    cur.execute("select rs.stop_no,s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(train_dict['no'],train_dict['to'],))
    flag=cur.fetchone()
    to_id=flag['station_id']
    to=flag['stop_no']

    cur.execute("select available_days from train_days where train_no=%s",(train_dict['no'],))
    information['available_days']=cur.fetchone()['available_days']

    for i in range(fromind,toind):
        age=str(i)+'age'
        name=str(i)+'name'
        gen=str(i)+'gender'
        pnr=generate_pnr()
        information['pnr_no'].append(pnr)
        date=datetime.strptime(train_dict['date'][:-3],"%a, %d %b %Y %H:%M:%S ")

        cur.execute("insert into passenger(pnr,passenger_name,age,gender) values(%s,%s,%s,%s)",(pnr,passenger_dict[name],passenger_dict[age],passenger_dict[gen],))
        mysql.connection.commit()
        cur.execute("insert into passenger_ticket values(%s,%s,%s,%s,%s)",(pnr,train_dict['t_class'],train_dict['rate'],fro_id,to_id,))
        mysql.connection.commit()
        cur.execute("insert into reservation values(%s,%s,%s,%s,%s,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"WL",date,))
        mysql.connection.commit()
    return information
