def smaller_than(date1,date2):#need to be format aaaa.mm.dd
                                #a year of format aaaa is always smaller
    #case aaaa
    if(len(date1)==4):
        return 1
    if(len(date2)==4):
        return 0
    #case
    m1=date1[5:7]
    d1=date1[8:]
    m2=date2[5:7]
    d2=date2[8:]

    if(m1<m2):
        return 1
    elif(m1>m2):
        return 0
    elif(m1==m2):
        if(d1<=d2):
            return 1
        else:
            return 0
