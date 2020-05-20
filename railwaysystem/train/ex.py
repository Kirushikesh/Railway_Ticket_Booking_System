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
"""def seat_availability(train_no,day,t_class,fro,to):
    file=open(str(train_no)+".txt")
    lists=file.readlines()
    i=0
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
                    seat=0
                    upto=k+skip1
                    while(k<upto):
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
                    return seat
                else:
                    j+=skip1+1
        else:
             i+=skip+1"""
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
        upto=j+skip
        while(j<upto):
            word=lists[j].split(',')
            skip1=int(word[1][:-1])
            #print(word)
            if(word[0]==t_class):
                k=j+1
                seat=0
                upto=k+skip1
                while(k<upto):
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
                a.append(seat)
            j+=skip1+1
        i+=skip+1
    return a
def book_train(train_no,day,t_class,fro,to):
    file=open(str(train_no)+".txt",'r')
    lists=file.readlines()
    i=0
    seat_no=-1
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
                            seat_no=k-j-1
                            for m in range(fro,to):
                                word[m]='1'
                            word[-1]+='\n'
                            lists[k]=','.join(word)
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
    file=open(str(train_no)+".txt",'w')
    file.writelines(lists)
    file.close()
    return seat_no
#print(seat_availability(1,'3A',2,3))
#print(book_train(1,'Monday','3A',2,3))
#store_train_classes(3,"147",3,{'1A':5,'2A':6,'3A':2,'SL':0})