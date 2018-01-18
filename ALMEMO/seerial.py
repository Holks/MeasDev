# -*- coding: utf-8 -*-

import json  # MOIS api andmete t6lgendamiseks
from time import sleep  # pollimise intervalli tarbeks
import urllib.request  # MOIS api jaoks
import sys
import glob
import serial  # seriali teek
from serial.serialutil import SerialException

#NB! PyCRC on vaja lisada.

from PyCRC.CRC16 import CRC16  # CRC
import threading
import queue
from time import sleep
import tkinter
from tkinter import messagebox
import io

''' 
programm avad COM pordi, ootab seeriali sisendit loeb seni andmeid serialist kuni puhver tyhi
kontrollib QRkoodi pikkust ja CRC-d (vajalik kuna kasutusel demo programmiversioon, mis annad juhuslikult andmer2mpsu ja ka kui QR-kood on liialt riknenud, et ei ole enam loetav
loob m66tevahendi klassi objekti{tunnistus, kuup2ev, MVid, KlientID, crckood, ja v6ibolla veel midagi}
objekti saab hiljem kasutada defandmete t2itmiseks jms

''' 


class SerialThread(threading.Thread):    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data=None
        self.queue = queue
        
    def ava_seerial(self, port):
        try:
            print( "Yhendan " + str(port[0]) )
            self.ser = serial.Serial(port[0], port[1],bytesize=8, parity='N', stopbits=1,
                   timeout=1)
            self.sio = io.TextIOWrapper(io.BufferedReader(self.ser, 1))#,write_through=False)#, newline="\x03")
            #self.sio._CHUNK_SIZE = 1
            print(str(port[0]) + " yhendatud")
            return False
        
        except SerialException:
            tkinter.messagebox.showinfo("Error", "COM kinni")  
            return True
            
    def write_serial(self, data):  
        self.data =  data#+"\r" # lisa carriage return rea l6ppu
        
        
    def run(self):
        while True:
            try:
            
                if self.ser.inWaiting(): # kui on sisendis andmeid
                    
                    text = self.sio.readline() # loe sisse rida
                    
                    if text != -1 and text.find('\x03') == -1: # kui ei ole tyhi ja ei sisalda ETX eritähemärki
                        self.queue.put(text) # pane järjekorda
                    else:
                        pass
                        #tkinter.messagebox.showinfo("Error", "Ei olnud korrektne sisendkood")
                if self.data:
                    self.ser.write(self.data.encode()) # kirjuta seeriali
                    print("kirjutan porti {0} teksti - \"{1}\r\"".format(self.ser.port,self.data))
                    self.data=None # reset v2ljund andmete muutujale
                    self.sio.flush()
            except:
                pass
        
        
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
