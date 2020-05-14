from railwaysystem import mysql,login_manager
import calendar
from flask_login import UserMixin

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
        temp['available_days']=i['available_days']
        
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

        information.append(temp)

    return information
def searchby_name_no(name_no):
    cur=mysql.connection.cursor()
    try:
        train_no=int(name_no)
        flag=cur.execute("select * from train where train_no = %s",(train_no,))
        if(flag):
            return cur.fetchone()
        else:
            return False
    except:
        train_name=name_no
        flag=cur.execute("select * from train where train_name = %s",(train_name,))
        if(flag):
            return cur.fetchone()
        else:
            return False

def search_station(station_name):
    cur=mysql.connection.cursor()
    cur.execute("select station_id from station where station_name = %s",(station_name,))
    id=cur.fetchone()['station_id']
    cur.execute("select train_no from route_has_station where station_id = %s",(id,))
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