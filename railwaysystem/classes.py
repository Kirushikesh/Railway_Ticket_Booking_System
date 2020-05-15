def initialise(dic,inter_stations,dicto):
    for key,value in dicto.items():
        dic[key]=[]
        for i in range(value):
            dic[key].append(['0']*inter_stations)
def return_seat_index(lis,fro,to):
    for i in range(len(lis)):
        flag=0
        for j in range(fro,to):
            if(lis[i][j]==1):
                flag=1
                break
        if(flag==0):
            break
    if(flag==1):
        return -1
    return i
def no_of_seats(lis,fro,to):
    no=0
    for i in range(len(lis)):
        flag=0
        for j in range(fro,to):
            if(lis[i][j]==1):
                flag=1
                break
        if(flag==0):
            no+=1
    return no
class base:
    alldays={}
    def __init__(self,days_availability,inter_stations,dic_seats):
        if('1' in days_availability):
            self.alldays['Sunday']={}
            initialise(self.alldays['Sunday'],inter_stations,dic_seats)
        if('2' in days_availability):
            self.alldays['Monday']={}
            initialise(self.alldays['Monday'],inter_stations,dic_seats)
        if('3' in days_availability):
            self.alldays['Tuesday']={}
            initialise(self.alldays['Tuesday'],inter_stations,dic_seats)
        if('4' in days_availability):
            self.alldays['Wednesday']={}
            initialise(self.alldays['Wednesday'],inter_stations,dic_seats)
        if('5' in days_availability):
            self.alldays['Thursday']={}
            initialise(self.alldays['Thursday'],inter_stations,dic_seats)
        if('6' in days_availability):
            self.alldays['Friday']={}
            initialise(self.alldays['Friday'],inter_stations,dic_seats)
        if('7' in days_availability):
            self.alldays['Saturday']={}
            initialise(self.alldays['Saturday'],inter_stations,dic_seats)
    
    def book_day(self,day,from_sta,to_sta,train_class):
        n=no_of_seats(self.alldays[day][train_class],from_sta,to_sta)
        if(n>0):
            seat=return_seat_index(self.alldays[day][train_class],from_sta,to_sta)
            print('Booking the seat wait for a while')
            for j in range(from_sta,to_sta):
                self.alldays[day][train_class][seat][j]=1
            print('Booked the seat')
            print('Seat no',train_class,' : ',str(seat),'On day',day)
        else:
            print('All seats are Full')
    def available_seats(self,day,fro,to,train_class):
        noofseat=no_of_seats(self.alldays[day][train_class],fro,to)
        if(noofseat==0):
            print('Seats are not available')
        else:
            print('Seats are present with ',str(noofseat),' no of seats')

"""d={'1a':2,'2a':2,'3a':2,'sl':2}
my=base('13',3,d)  
my.available_seats('Tuesday',0,2,'1a')
my.book_day('Tuesday',0,2,'1a')
my.available_seats('Tuesday',0,2,'1a')
my.book_day('Tuesday',0,2,'1a')
my.available_seats('Tuesday',0,2,'1a')
my.book_day('Tuesday',0,2,'1a')
my.available_seats('Tuesday',0,2,'sl')
my.book_day('Tuesday',2,3,'1a')"""

d={'1a':2,'2a':2,'3a':2,'sl':2}
main={}
main[12345]=base('13',3,d)
main[12456]=base('237',4,d)
print(main[12345].alldays['Sunday'])