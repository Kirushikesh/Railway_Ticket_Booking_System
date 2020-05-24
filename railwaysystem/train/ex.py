def create_file(filename):
    file=open(str(filename)+".txt",'w')
    return file
def initialise(day,file,station,dicto):
    length=len(dicto)
    for key,value in dicto.items():
        length+=value
    file.write(day+','+str(length)+"\n")
    for key,value in dicto.items():
        file.write(key+","+str(value)+"\n")
        for i in range(value):
            ch="0,"*(station-1)+"0\n"
            file.write(ch)
def store_train_classes(trainno,days_availability,no_inter_sta,dicto):
    file=create_file(trainno)
    if('1' in days_availability):
        initialise("Sunday",file,no_inter_sta,dicto)
    if('2' in days_availability):
        initialise("Monday",file,no_inter_sta,dicto)
    if('3' in days_availability):
        initialise("Tuesday",file,no_inter_sta,dicto)
    if('4' in days_availability):
        initialise("Wednesday",file,no_inter_sta,dicto)
    if('5' in days_availability):
        initialise("Thursday",file,no_inter_sta,dicto)
    if('6' in days_availability):
        initialise("Friday",file,no_inter_sta,dicto)
    if('7' in days_availability):
        initialise("Satuday",file,no_inter_sta,dicto)
def seat_availability_onthatday(train_no,day,t_class,fro,to):
    file=open(str(train_no)+".txt")
    lists=file.readlines()
    i=0
    while(i<len(lists)):
        word=lists[i].split(',')
        skip=int(word[1][:-1])
        if(word[0]==day):
            j=i+1
            upto=j+skip
            check=0
            while(j<upto):
                word=lists[j].split(',')
                skip1=int(word[1][:-1])
                #print(word,j)
                if(word[0]==t_class):
                    k=j+1
                    seat=0
                    upto1=k+skip1
                    while(k<upto1):
                        flag=0
                        word=lists[k].split(',')
                        word[-1]=word[-1][:-1]
                        for m in range(fro,to):
                            if(word[m]=='1'):
                                flag=1
                                break
                        if(flag==0):
                            seat+=1
                        k+=1
                    if(seat>0):
                        return seat
                    else:
                        check=1
                elif(word[0]==t_class+'_R'):
                    k=j+1
                    seat=0
                    upto1=k+skip1
                    while(k<upto1):
                        flag=0
                        word=lists[k].split(',')
                        word[-1]=word[-1][:-1]
                        stri=''
                        for m in range(fro,to):
                            stri+=word[m]
                        if(int(stri)==0):
                            seat-=2
                        elif('2' in stri):
                            pass
                        else:
                            seat-=1
                        k+=1
                    if(seat<0):
                        return seat
                    else:
                        check=1
                elif(check==1):
                    return 'NaN'
                j+=skip1+1
                #print(j)
        else:
             i+=skip+1
def seat_availability(train_no,t_class,fro,to):
    file=open(str(train_no)+".txt")
    lists=file.readlines()
    i=0
    a=[]
    while(i<len(lists)):
        word=lists[i].split(',')
        skip=int(word[1][:-1])
        #print(word)
        j=i+1
        check=0
        upto=j+skip
        while(j<upto):
            word=lists[j].split(',')
            skip1=int(word[1][:-1])
            #print(word)
            if(word[0]==t_class):
                k=j+1
                seat=0
                upto1=k+skip1
                while(k<upto1):
                    flag=0
                    word=lists[k].split(',')
                    word[-1]=word[-1][:-1]
                    #print(word)
                    for m in range(fro,to):
                        if(word[m]=='1'):
                            flag=1
                            break
                    if(flag==0):
                        seat+=1
                    k+=1
                #print(seat)
                if(seat>0):
                    a.append(seat)
                else:
                    check=1
            #print(check)
            elif(word[0]==t_class+'_R' and check==1):
                k=j+1
                seat=0
                upto1=k+skip1
                while(k<upto1):
                    flag=0
                    word=lists[k].split(',')
                    word[-1]=word[-1][:-1]
                    #print(word)
                    stri=''
                    for m in range(fro,to):
                        stri+=word[m]
                    if(int(stri)==0):
                        seat-=2
                    elif('2' in stri):
                        pass
                    else:
                        seat-=1
                    k+=1
                #print(seat)
                if(seat<0):
                    a.append(seat)
                else:
                    a.append('NaN')
                check=0
            elif(check==1):
                #print(t_class)
                a.append('NaN')
                check=0
            j+=skip1+1
        i+=skip+1
    return a
def book_train(train_no,day,t_class,fro,to,noofpass):
    file=open(str(train_no)+".txt",'r')
    lists=file.readlines()
    i=0
    seat_no=[]
    flag=1
    while(i<len(lists)):
        word=lists[i].split(',')
        skip=int(word[1][:-1])
        if(word[0]==day):
            j=i+1
            upto=j+skip
            while(j<upto):
                word=lists[j].split(',')
                skip1=int(word[1][:-1])
                if(word[0]==t_class):
                    k=j+1
                    upto=k+skip1
                    #print(word,j)
                    if(t_class[-2:]!='_R'):
                        while(k<upto):
                            flag=0
                            word=lists[k].split(',')
                            word[-1]=word[-1][:-1]
                            #print(word,k)
                            for m in range(fro,to):
                                if(word[m]=='1'):
                                    flag=1
                                    break
                            if(flag==0):
                                if(noofpass>0):
                                    seat_no.append(k-j-1)
                                    noofpass-=1
                                    for m in range(fro,to):
                                        word[m]='1'
                                    word[-1]+='\n'
                                        #print(word)
                                    lists[k]=','.join(word)
                                else:
                                    break
                            k+=1
                    else:
                        while(k<upto):
                            flag=0
                            word=lists[k].split(',')
                            word[-1]=word[-1][:-1]
                            word=list(map(int,word))
                            #print(word,k)
                            for m in range(fro,to):
                                if(word[m]==2):
                                    flag=2
                                    break
                                elif(word[m]==1):
                                    flag=1
                            
                            #print(flag,word,noofpass,k,upto)
                            
                            if(noofpass>=2 and flag==0):
                                seat_no.append(k-j-1)
                                seat_no.append(k-j-1)
                                noofpass-=2
                                for m in range(fro,to):
                                    word[m]+=2
                                word=list(map(str,word))
                                word[-1]+='\n'
                                        #print(word)
                                lists[k]=','.join(word)
                            elif((noofpass>=1 or flag==1) and flag!=2):
                                seat_no.append(k-j-1)
                                noofpass-=1
                                for m in range(fro,to):
                                    word[m]+=1
                                word=list(map(str,word))
                                word[-1]+='\n'
                                    #print(word)
                                lists[k]=','.join(word)
                            if(noofpass==0):
                                break
                            k+=1
                    if(k==upto-1):
                        flag=0
                if(flag==0):
                    break
                else:
                    j+=skip1+1
        if(flag==0):
            break 
        else:
           i+=skip+1
    file.close()
    #print(lists)
    file=open(str(train_no)+".txt",'w')
    file.writelines(lists)
    file.close()
    return seat_no

def no_rac_booked(train_no,day,t_class,fro,to):
    file=open(str(train_no)+".txt")
    lists=file.readlines()
    i=0
    while(i<len(lists)):
        word=lists[i].split(',')
        skip=int(word[1][:-1])
        if(word[0]==day):
            j=i+1
            upto=j+skip
            check=0
            while(j<upto):
                word=lists[j].split(',')
                skip1=int(word[1][:-1])
                #print(word,j)
                if(word[0]==t_class):
                    k=j+1
                    booked=0
                    upto1=k+skip1
                    while(k<upto1):
                        flag=0
                        word=lists[k].split(',')
                        word[-1]=word[-1][:-1]
                        for m in range(fro,to):
                            if(word[m]=='2'):
                                flag=2
                                break
                            elif(word[m]=='1'):
                                flag=1
                        if(flag==2):
                            booked+=2
                        elif(flag==1):
                            booked+=1
                        k+=1
                    return booked
                j+=skip1+1
                #print(j)
        else:
             i+=skip+1
#print(seat_availability_onthatday(1,'Sunday','3A',0,2))
#print(seat_availability(1,'3A',0,2))
#print(book_train(1,'Sunday','3A_R',0,2,2))
#store_train_classes(1,"123",3,{'1A':5,'2A':4,'2A_R':2,'3A':4,'3A_R':2,'SL':5,'SL_R':3})
#store_train_classes(2,"347",2,{'1A':0,'2A':4,'2A_R':3,'3A':3,'3A_R':1,'SL':3,'SL_R':1})
#store_train_classes(3,"147",3,{'1A':5,'2A':6,'2A_R':4,'3A':2,'3A_R':1,'SL':0,'SL_R':0})