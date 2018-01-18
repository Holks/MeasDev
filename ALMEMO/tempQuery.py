# -*- coding: utf-8 -*-
'''
Created on 4. dets 2017

@author: holger
'''
import serial  # seriali teek
from serial.serialutil import SerialException
import io
from time import sleep
import configparser
import os

ser = serial.Serial('COM19', 9600 ,bytesize=8, parity='N', stopbits=1, timeout=1)
#sio = io.TextIOWrapper(io.BufferedReader(ser, 1))
ser.write('S1'.encode())
sleep(0.5)
#if ser.inWaiting(): # kui on sisendis andmeid                    
text = ser.readline() # loe sisse rida
text = ser.readline() # loe sisse rida
print(str(text))
text = str(text).split(';')
print(text)
cwd = os.getcwd()
cfgfile = open(cwd+"/temp.ini",'w')
Config = configparser.ConfigParser()
Config.add_section('temperatuurid')
for i in range(8):
    Config.set('temperatuurid','T'+str(i),text[2+i])
Config.add_section('keskkond')
Config.set('keskkond','Keskkonna_temp',text[10])
Config.set('keskkond','Keskkonna_niiskus',text[20])
Config.write(cfgfile)
cfgfile.close()