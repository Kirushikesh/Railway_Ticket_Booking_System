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
        #cur=mysql.connection.cursor()
        #cur.execute("UPDATE users SET username = %s , email = %s WHERE id = %s",(self.username,self.email,self.id,))

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
        cur.execute("select train_no from train where train_name = %s",(train_name,))
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
    if isinstance(o, datetime):
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

    #print
    cur.execute("select rs.stop_no,s.station_id from station as s join route_has_station as rs on s.station_id=rs.station_id where rs.train_no=%s and s.station_name=%s",(train_dict['no'],train_dict['to'],))
    flag=cur.fetchone()
    to_id=flag['station_id']
    to=flag['stop_no']

    if(book_class[-2:]=='_R'):
        status_no=tex.no_rac_booked(train_dict['no'],return_full_day(train_dict['day']),book_class,fro,to)
        status_no+=1
        #print(status_no)

    information['seatno']=tex.book_train(train_dict['no'],return_full_day(train_dict['day']),book_class,fro,to,noofpass)
    cur.execute("select available_days,train_name from train_days join train on train_days.train_no=train.train_no where train.train_no=%s",(train_dict['no'],))
    flag=cur.fetchone()
    information['available_days']=flag['available_days']
    information['train_name']=flag['train_name']
    information['class']=book_class
    information['status_no']=[]

    flag=0
    for i in range(fromind,toind):
        age=str(i)+'age'
        name=str(i)+'name'
        gen=str(i)+'gender'
        pnr=generate_pnr()
        information['pnr_no'].append(pnr)
        cur.execute("insert into passenger values(%s,%s,%s,%s,%s)",(pnr,information['seatno'][flag],passenger_dict[name],passenger_dict[age],passenger_dict[gen],))
        mysql.connection.commit()
        date=train_dict['date']

        if(book_class[-2:]!='_R'):
            cur.execute("insert into passenger_ticket values(%s,%s,%s,%s,%s)",(pnr,book_class,train_dict['rate'],fro_id,to_id,))
            mysql.connection.commit()
            information['status_no'].append(0)
            cur.execute("insert into reservation values(%s,%s,%s,%s,%s,0,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"CNF",date,))
        else:
            cur.execute("insert into passenger_ticket values(%s,%s,%s,%s,%s)",(pnr,book_class[:-2],train_dict['rate'],fro_id,to_id,))
            mysql.connection.commit()
            information['status_no'].append(status_no)
            cur.execute("insert into reservation values(%s,%s,%s,%s,%s,%s,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"RAC",status_no,date,))
            status_no+=1
        
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

    try:
        day=datetime.strptime(day[:-3],"%a, %d %b %Y %H:%M:%S ")
    finally:
        #print(trainno,day,t_class,fro,to)
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

    information['seatno']=[]
    cur.execute("select available_days,train_name from train_days join train on train_days.train_no=train.train_no where train.train_no=%s",(train_dict['no'],))
    flag=cur.fetchone()
    information['available_days']=flag['available_days']
    information['train_name']=flag['train_name']
    information['class']="WL"
    status=no_of_wl(int(train_dict['no']),train_dict['date'],fro,to,train_dict['t_class'])+1
    information['status_no']=[]

    for i in range(fromind,toind):
        age=str(i)+'age'
        name=str(i)+'name'
        gen=str(i)+'gender'
        pnr=generate_pnr()
        information['pnr_no'].append(pnr)
        date=train_dict['date']
        information['seatno'].append('NaN')

        cur.execute("insert into passenger(pnr,passenger_name,age,gender) values(%s,%s,%s,%s)",(pnr,passenger_dict[name],passenger_dict[age],passenger_dict[gen],))
        mysql.connection.commit()
        cur.execute("insert into passenger_ticket values(%s,%s,%s,%s,%s)",(pnr,train_dict['t_class'],train_dict['rate'],fro_id,to_id,))
        mysql.connection.commit()
        information['status_no'].append(status)
        cur.execute("insert into reservation values(%s,%s,%s,%s,%s,%s,%s)",(current_user.email_id,pnr,int(train_dict['no']),information['available_days'],"WL",status,date,))
        mysql.connection.commit()
        status+=1

    return information

def return_pnrdetails(pnr):
    cur=mysql.connection.cursor()
    cur.execute("""select * from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on 
                pt.pnr=r.pnr where p.pnr=%s""",(pnr,))
    flag = cur.fetchone()
    cur.execute("select train_name from train where train_no=%s",(flag['train_no'],))
    flag['train_name']=cur.fetchone()['train_name']
    flag['from_name']=get_station_name(flag['source_id'])[0]
    flag['to_name']=get_station_name(flag['destination_id'])[0]
    cur.execute("select user_name from user where email_id=%s",(flag['email_id'],))
    flag['user_name']=cur.fetchone()['user_name']
    return flag

def cancel_ticket(pnr):
    cur=mysql.connection.cursor()
    cur.execute("""select r.train_no,r.reservation_date,pt.source_id,pt.destination_id,r.reservation_status,p.seat_no,pt.class_type,r.status_no
                from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on pt.pnr=r.pnr where p.pnr=%s""",(pnr,))
    cancel=cur.fetchone()

    date=cancel['reservation_date']
    date=date.isoweekday()
    date=date+1
    if(date==8):
        date=1
    day=return_full_day(convert_no_week(str(date))[0])

    from_stopno,to_stopno=return_stop_no(cancel['train_no'],get_station_name(cancel['source_id'])[0],get_station_name(cancel['destination_id'])[0])
    
    if(cancel['class_type']=='1A'):
        cur.execute("""select r.pnr,r.status_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                        pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='WL' and r.reservation_date=%s and pt.class_type=%s and
                        pt.source_id=%s and pt.destination_id=%s order by r.status_no asc""",(cancel['train_no'],cancel['reservation_date'],
                        cancel['class_type'],cancel['source_id'],cancel['destination_id'],))        
        change=cur.fetchall()
        if(change):
            cur.execute("update reservation set status_no=0,reservation_status='CNF' where pnr=%s",(change[0]['pnr'],))
            mysql.connection.commit()
            cur.execute("update passenger set seat_no=%s where pnr=%s",(cancel['seat_no'],change[0]['pnr'],))
            mysql.connection.commit()

            for i in range(1,len(change)):
                cur.execute("update reservation set status_no=%s where pnr=%s",(change[i]['status_no']-1,change[i]['pnr'],))
                mysql.connection.commit()

        else:
            tex.cancel_booking(cancel['train_no'],day,cancel['class_type'],from_stopno,to_stopno,cancel['seat_no'])

    if(cancel['reservation_status']=='WL'):
        cur.execute("""select r.pnr,r.status_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                        pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='WL' and r.reservation_date=%s and pt.class_type=%s and
                        pt.source_id=%s and pt.destination_id=%s and r.status_no > %s""",(cancel['train_no'],
                        cancel['reservation_date'],cancel['class_type'],cancel['source_id'],cancel['destination_id'],cancel['status_no'],))
        change=cur.fetchall()
        if(change):
            for i in change:
                cur.execute("update reservation set status_no=%s where pnr=%s",(i['status_no']-1,i['pnr'],))
                mysql.connection.commit()

    elif(cancel['reservation_status']=='RAC'):
        cur.execute("""select r.pnr,r.status_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                        pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='RAC' and r.reservation_date=%s and pt.class_type=%s and
                        pt.source_id=%s and pt.destination_id=%s and r.status_no > %s order by r.status_no asc""",(cancel['train_no'],
                        cancel['reservation_date'],cancel['class_type'],cancel['source_id'],cancel['destination_id'],cancel['status_no'],))
        change1=cur.fetchall()

        if(change1):
            for i in change1:
                cur.execute("update reservation set status_no=%s where pnr=%s",(i['status_no']-1,i['pnr'],))
                mysql.connection.commit()
            cur.execute("""select r.pnr,r.status_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                            pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='WL' and r.reservation_date=%s and pt.class_type=%s and
                            pt.source_id=%s and pt.destination_id=%s order by r.status_no asc""",(cancel['train_no'],cancel['reservation_date'],
                            cancel['class_type'],cancel['source_id'],cancel['destination_id'],))
            change2=cur.fetchall()
            if(change2):
                #print(change1,change2)
                cur.execute("update reservation set status_no=%s,reservation_status='RAC' where pnr=%s",(change1[-1]['status_no'],change2[0]['pnr'],))
                mysql.connection.commit()
                cur.execute("update passenger set seat_no=%s where pnr=%s",(cancel['seat_no'],change2[0]['pnr'],))
                mysql.connection.commit()
                for i in range(1,len(change2)):
                    cur.execute("update reservation set status_no=%s where pnr=%s",(change2[i]['status_no']-1,change2[i]['pnr'],))
                    mysql.connection.commit()
            else:
                #print(a[2])
                tex.cancel_booking(cancel['train_no'],day,cancel['class_type']+'_R',from_stopno,to_stopno,cancel['seat_no'])
        
        else:
            tex.cancel_booking(cancel['train_no'],day,cancel['class_type']+'_R',from_stopno,to_stopno,cancel['seat_no'])
    else:
        cur.execute("""select r.pnr,r.status_no,p.seat_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                        pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='RAC' and r.reservation_date=%s and pt.class_type=%s and
                        pt.source_id=%s and pt.destination_id=%s order by r.status_no asc""",(cancel['train_no'],
                        cancel['reservation_date'],cancel['class_type'],cancel['source_id'],cancel['destination_id'],))
        change1=cur.fetchall()

        if(change1):
            cur.execute("update reservation set status_no=0,reservation_status='CNF' where pnr=%s",(change1[0]['pnr'],))
            mysql.connection.commit()
            cur.execute("update passenger set seat_no=%s where pnr=%s",(cancel['seat_no'],change1[0]['pnr'],))
            mysql.connection.commit()

            for i in range(1,len(change1)):
                cur.execute("update reservation set status_no=%s where pnr=%s",(change1[i]['status_no']-1,change1[i]['pnr'],))
                mysql.connection.commit()

            cur.execute("""select r.pnr,r.status_no from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on
                            pt.pnr=r.pnr where r.train_no=%s and r.reservation_status='WL' and r.reservation_date=%s and pt.class_type=%s and
                            pt.source_id=%s and pt.destination_id=%s order by r.status_no asc""",(cancel['train_no'],cancel['reservation_date'],
                            cancel['class_type'],cancel['source_id'],cancel['destination_id'],))
            change2=cur.fetchall()
            if(change2):
                cur.execute("update reservation set status_no=%s,reservation_status='RAC' where pnr=%s",(change1[-1]['status_no'],change2[0]['pnr'],))
                mysql.connection.commit()
                cur.execute("update passenger set seat_no=%s where pnr=%s",(change1[0]['seat_no'],change2[0]['pnr'],))
                mysql.connection.commit()
                for i in range(1,len(change2)):
                    cur.execute("update reservation set status_no=%s where pnr=%s",(change2[i]['status_no']-1,change2[i]['pnr'],))
                    mysql.connection.commit()
            else:
                tex.cancel_booking(cancel['train_no'],day,cancel['class_type']+'_R',from_stopno,to_stopno,change1[0]['seat_no'])
        else:
            tex.cancel_booking(cancel['train_no'],day,cancel['class_type'],from_stopno,to_stopno,cancel['seat_no'])

    cur.execute("delete reservation,passenger_ticket from reservation join passenger_ticket on reservation.pnr=passenger_ticket.pnr where reservation.pnr=%s",(pnr,))
    mysql.connection.commit()
    cur.execute("delete from passenger where pnr=%s",(pnr,))
    mysql.connection.commit()

def mybooking_user(email_id):
    cur=mysql.connection.cursor()
    cur.execute("""select * from passenger as p join passenger_ticket as pt on p.pnr=pt.pnr join reservation as r on pt.pnr=r.pnr where r.email_id=%s""",(email_id,))
    flag=cur.fetchall()
    for i in flag:
        i['source_id']=get_station_name(i['source_id'])[0]
        i['destination_id']=get_station_name(i['destination_id'])[0]
    return flag