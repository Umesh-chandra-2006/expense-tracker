a=input()
b=[]
for i in range(len(a)-1,-1,-1):
    if(a[i].isalpha()):
        b.append(a[i])
for i in range(len(a)):
    if(not a[i].isalnum()):
        b.insert(i,a[i])
print(''.join(b))

