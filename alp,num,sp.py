a=input()
b=''
c=''
d=''
for i in a:
    if(i.isalpha()):
        b=b+i
    elif(i.isdigit()):
        c=c+i
    else:
        d=d+i
    print(b,c,d)