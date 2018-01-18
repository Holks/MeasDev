# -*- coding: utf-8 -*-
'''
Created on 18. mai 2017

@author: holger
'''
import re


output = open('resultspöördlaud.csv','w')
f = open("C:\\Users\\holger\\Desktop\\WinAMC\\datalog.txt", 'r')
for line in f:
    line = line.strip()
    
    splittedLine = re.split(r'[°\'\" \t]+', line)
    print(splittedLine)
    nurk = splittedLine[2].split("ŗ")[0]
    print(nurk)
    kraad = splittedLine[2].split("ŗ")[0]
    minut = splittedLine[2].split("ŗ")[1]
    sekund = splittedLine[3]
    if(splittedLine[2][0] == "-"):
        
        nurk = -1*(float(kraad)+float(minut)/60 + float(sekund)/3600)
        print(nurk)
    else:
        nurk = float(kraad)+float(minut)/60 + float(sekund)/3600
        print(nurk)
    output.write(str(nurk).replace(".", ",")+"\n")
    print(nurk)
f.close()
output.close()