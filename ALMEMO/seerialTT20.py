# -*- coding: utf-8 -*-

import serial  # seriali teek
from serial.serialutil import SerialException

#NB! PyCRC on vaja lisada.

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


class SerialThreadTT20(threading.Thread):    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data=None
        self.queue = queue
        
    def ava_seerial(self, port):
        try:
            try:
                self.ser = serial.Serial(port=port[0], baudrate=4800,
                                      bytesize=7, parity='E', stopbits=2,
                                      timeout=0.2, xonxoff=0, rtscts=0)
            except  serial.SerialException as ex:
                print('Port {0} is unavailable: {1}'.format(port, ex))
                return True # tagasi veateatega
            ###self._conn = io.TextIOWrapper(io.BufferedRWPair(self._fw, self._fw, 1), encoding=None,newline='\r')
            ###self._conn=serial.Serial(port,4800,parity="E",stopbits=2,bytesize=7)
            self.ser.setDTR(1)
            self.ser.setRTS(0)
            self.ser.flush()
            self.sio = io.TextIOWrapper(io.BufferedReader(self.ser, 1))#,write_through=False)#, newline="\x03")
            #self.sio._CHUNK_SIZE = 1
            print(str(port[0]) + " yhendatud")
            return False
        
        except SerialException:
            tkinter.messagebox.showinfo("Error", "COM kinni")  
            return True
            

        
    def getId(self):
        self.write("ID?")
        return self.read()
    
    def write_serial(self, data):  
        self.data =  data#+"\r" # lisa carriage return rea l6ppu
          
    def write(self, data):        
        self.ser.write(('%s\r'%data).encode())
        print("kirjutan porti {0} teksti - \"{1}\r\"".format(self.ser.port, data))
        self.ser.flush()
        
    def read(self):
        #res = self._conn.read(2048)
        #print 'read=',res,repr(res)
        res=self.sio.readline()
        self.sio.flush() 
        print( 'read=',res)
        return('%s'%res.strip())
    
    def run(self):
        while True:
            #try:
                if self.ser.inWaiting(): # kui on sisendis andmeid                    
                    text = self.sio.readline() # loe sisse rida
                    print(text)
                    self.sio.flush()
                    if text != -1: #and text.find('\x03') == -1: # kui ei ole tyhi ja ei sisalda ETX eritähemärki
                        self.queue.put(text) # pane järjekorda
                    else:
                        pass
                        #tkinter.messagebox.showinfo("Error", "Ei olnud korrektne sisendkood")
                if self.data:
                    self.ser.write(('%s\r'%self.data).encode()) # kirjuta seeriali
                    #print("kirjutan porti {0} teksti - \"{1}\r\"".format(self.ser.port, self.data))
                    self.data=None
                    self.ser.flush()
            #except:
             #   pass
        
    def close(self):
        self.ser.close()    