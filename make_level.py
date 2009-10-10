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
        row.append(random.randint(1,5))
        n+=1
        

    level.append(row)
    row=[]
    i+=1
    n = 0

data = ""
x2 = 0
y2 = 0
for row in level:
    for col in row:
        data += str(col)
        
        data += " "
            
        x2+=1
    data = data[:-1] 
    data += "\n"
    x2=0
    y2+=1



f = open("level", "w")

f.write(data)
