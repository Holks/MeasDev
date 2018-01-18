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


''' 
programm avad COM pordi, ootab seeriali sisendit loeb seni andmeid serialist kuni puhver tyhi
kontrollib QRkoodi pikkust ja CRC-d (vajalik kuna kasutusel demo programmiversioon, mis annad juhuslikult andmer2mpsu ja ka kui QR-kood on liialt riknenud, et ei ole enam loetav
loob m66tevahendi klassi objekti{tunnistus, kuup2ev, MVid, KlientID, crckood, ja v6ibolla veel midagi}
objekti saab hiljem kasutada defandmete t2itmiseks jms

''' 


class SerialThread(threading.Thread):    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        
    def ava_seerial(self, port):
        try:
            self.ser = serial.Serial(port[0], port[1],timeout=0.2)
            self.ser.flush()
            text = self.ser.readline()
            text = self.ser.readline()
            text = self.ser.readline()
        except SerialException:
            tkinter.messagebox.showinfo("Error", "COM kinni")  
        
    def run(self):
        while True:
            try:
                if self.ser.inWaiting():
                    text = self.ser.readline()
                    if text != -1:
                        self.queue.put(text)
                    else:
                        tkinter.messagebox.showinfo("Error", "Ei olnud korrektne sisendkood")
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
