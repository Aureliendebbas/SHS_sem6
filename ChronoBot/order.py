from smaller_than import smaller_than

def order(text):#ça ordonne un text
    text1=text.split('\n')
    #separate events from other useless lines in the page
    newtext=[]
    craptext=[]
    for line in text1:
        if (line[:3]=='*[[') and (line[3:7].isnumeric()):
            newtext.append(line)
        else:
            craptext.append(line)
    
    #case where page is empty, only has one line in it, or only has crap in it
    if len(newtext)<2:
        return text

    #check for repeated lines
    provisional=[]
    for line in newtext:
        if line not in provisional:
            provisional.append(line)   
    newtext=provisional
    
    ok=0
    while(ok==0):
        ok=1
        for i in range(len(newtext)-1):
            pos1  = newtext[i].find(']]')
            date1 = newtext[i][3:pos1]
            pos2  = newtext[i+1].find(']]')
            date2 = newtext[i+1][3:pos2]
            if not smaller_than(date1,date2):
                ok=0
                event=newtext[i]
                newtext[i]=newtext[i+1]
                newtext[i+1]=event

    newtext='\n'.join(newtext)+'\n'+'\n'.join(craptext)
    return newtext
