# -*- coding: utf-8 -*-
'''
Created on 18. mai 2017

@author: holger
'''
import serial  # seriali teek
from serial.serialutil import SerialException
import sys
import glob
import time

def loo_seerial_yhendus(baudrate, port, timeout): # TODO: kontrollida vajalikkus
    ser = serial.Serial()
    ser.baudrate = baudrate
    ser.port = port  # siia sobiv com pordi aadress
    ser.timeout = timeout  # timeout kui peaks serialiga probleeme olema
    return ser

def otsi_seerial():
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(50)] #otsib porte kuni 356-ni
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
    
        result = []
        for port in ports: # kontrollib, kas port on vaba
            try: # annab exceptoioni kui port ei ole vaba
                s = serial.Serial(port)
                s.close()   
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    
ser = loo_seerial_yhendus(19200, 'COM17', 0.1)
ser.open() 
results = []
value1 = time.time()
output = open('resultsELKOMAT.csv','w')
output.write("X;Y\n")
for i in range(0,  3800):
    ser.write("a\r".encode('utf-8')) 
    data = ser.readline()
    if len(data) > 0:
        lugem = data.split()
        if len(lugem) == 4:
            lugemX =float(lugem[2].decode('utf-8'))#.replace('.',','))
            lugemY = float(lugem[3].decode('utf-8'))#.replace('.',','))
            if lugemX != 0 and lugemY != 0:
                results.append([lugemX,lugemY])
                print(lugemX, lugemY)
for res in results:
    output.write(str(res[0]).replace('.',',')+";"+str(res[1]).replace('.',',') +"\n")
            # output.write(str(lugemX + lugemY) +"\n")
value2 = time.time()
print(value2-value1)
output.close()
