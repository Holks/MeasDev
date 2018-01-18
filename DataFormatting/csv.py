# -*- coding: utf-8 -*-
'''
Created on 29. mai 2017

@author: holger
'''
f = open('res.csv', 'r')
output = open('results.csv','w')
counter = 0
for line in f:
    if counter == 1 or counter%4 == 0:
        print(counter, counter%4)
        output.write(line)#+"\n")
    counter=counter+1

f.close()
output.close()