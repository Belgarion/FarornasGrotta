#!/usr/bin/env python

import random

x =raw_input("How many X? ")
x = int(x)

y =raw_input("How many Y? ")
y = int(y)

print y, x

level =[]
row =[]
i = 0
n = 0
while i < x:
    while n < y:
        row.append(random.randint(1,255))
        n+=1
        

    level.append(row)
    row=[]
    i+=1
    n = 0

print level
data = ""
x2 = 0
y2 = 0
for row in level:
    for col in row:
        data += str(col)
        
        if x2 is not x-1:
            data += " "
            
        x2+=1
    data += "\n"
    x2=0
    y2+=1


print data

f = open("level", "w")

f.write(data)
