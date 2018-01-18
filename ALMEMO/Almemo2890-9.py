# -*- coding: utf-8 -*-

import os
import pygubu # @UnresolvedImport
import threading
import serial  # seriali teek
from serial.serialutil import SerialException
from pynput import keyboard
import tkinter as tk
from tkinter import messagebox
import time
import queue
from datetime import datetime
import re
from seerial import SerialThread
from seerialTT20 import SerialThreadTT20
from seerial import otsi_seerial   # @UnresolvedImport
import win32com.client
import winsound
from pygubu.builder import ttkstdwidgets

shell = win32com.client.Dispatch("WScript.Shell")


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
           
class Smartsensor:
    
    def __init__(self, master): 
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()
        self.ser = ""    
        # 2: Load an ui file
        builder.add_from_file(os.path.dirname(os.path.realpath(__file__))+'\Almemo2890-9.ui')

        # 3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('main_frame', master)
        master.title("Almemo data input (logger) v ")
        master.minsize(width=410, height=145)
        
        # 4: impordi pygubu's defineeritud muutujad
        self.kiirus= builder.get_variable("almemoOutput")

        self.seadmeseerial = serial.Serial()
        self.valitud_seerial_port = builder.get_variable("valitud_seerial_port")
        
        # 5: impordi pygubu's defineeritud objektid
        self.combobox_seerial_pordid = builder.get_object("combobox_seerial_pordid", master)
        self.yhenduseTextTemp = builder.get_variable("yhenduseTextTemp")
        self.yhenduseTextSensor = builder.get_variable("yhenduseTextSensor")
        self.keskmistamine = builder.get_variable("keskmistamine")
        self.statusText = builder.get_variable("status_text")
        #self.enableOutput = False
        
        # 6 ühendab ui failis kirjeldatud tegevuste nimed funktsioonidega
        builder.connect_callbacks(self)

        self.window = master
        self.moisapi = False
        
        self.queue = queue.Queue()   
        self.thread = SerialThread(self.queue)
        self.thread.daemon = True
        
        self.queue2 = queue.Queue()   
        self.thread2 = SerialThreadTT20(self.queue2)
        self.thread2.daemon = True
        self.keylogger = threading.Thread()
        print(self.keylogger.isAlive())
        
        self.keylogger.daemon = True
        self.process_serial_called = False
        self.process_serial()
        
    def on_release(self, key):
        '''
        Funktsioon arvutiga ühendatud seadmega suhtlemiseks:
        'F12' klahvi peale arvuti küsib seadmelt käsuga (kirjutatud vastavasse lahtrisse) andmed ja edastab aktiivsele aknale
        
        '''
        global shell
        try: k = key.char # single-char keys
        except: k = key.name # other keys
        if key == keyboard.Key.esc: return False # stop listener # TODO: kontrollida vajalikkus
        if k in ['f9','f8']: # keys interested
            print("Vajutasid F9 v F8")
            if k == 'f9':
                self.thread.write_serial("S1") # kysi kõiki andmeid
            elif k=='f8':
                self.thread2.write_serial('?') # kysi kõiki andmeid
           # winsound.MessageBeep()  
              
        
    def clicked_on_leia_seerial_pordid(self, event=None):
        result = otsi_seerial()
        if result:
            self.combobox_seerial_pordid['values']=result
        else:
            tk.messagebox.showinfo("Viga", "Ei leidnud ühtegi vaba COM ühendust!\nKontrolli ühendusi!")

        
    def process_serial(self):
        self.process_serial_called= True
        while self.queue.qsize():
            try:
                print("Temp Kirje kuvamine")
                kirje = self.queue.get().strip() #.replace('\xf8','\xb0') # ja kraadimärgi asendamine
                self.kiirus.set(kirje) # kuvab kirje GUI infolahtris
                
                # siia peaks tulema esmane kirje töötlus, mis eemaldab ebavajaliku info 
                kirje = kirje.split(';') # tykeldan kirje andurite tulemusteks      
                outData =""          
                if self.keskmistamine.get(): # kui eksisteerib v2ljundi huvi, siis annab need välja
                    kirjete_loend = self.keskmistamine.get().strip().split(" ") # NB! tyhikuga eraldatud andmeväljad
                    try:
                        for sensor in kirjete_loend:
                            outData += kirje[int(sensor)+2].replace('.',',')+'\t'  # v2ljundkirje koostamine ja eraldamine tabulatsiooniga
                        shell.SendKeys(outData) # saadab sobiva anduri tulemused
                        print("Temperatuuri lugem" + outData)
                    except IndexError: # kui sisend ei ole piisava arvu liikmetega annab vea v6i logib selle
                        print("ei olnud korrektne sisend")
                        pass
                else:
                    pass
            except queue.Empty:
                pass
            
        while self.queue2.qsize():
            try:
                print("Sensori kirje kuvamine")
                kirje = self.queue2.get().strip() #.replace('\xf8','\xb0') # ja kraadimärgi asendamine
                self.kiirus.set(kirje) # kuvab kirje GUI infolahtris
                
                # siia peaks tulema esmane kirje töötlus, mis eemaldab ebavajaliku info 
                #kirje = kirje.split(';') # tykeldan kirje andurite tulemusteks      
                outData ="" 
                outData = kirje.replace('.',',')+'\t'  # v2ljundkirje koostamine ja eraldamine tabulatsiooniga
                shell.SendKeys(outData) # saadab sobiva anduri tulemused
                print("TT20 lugem" + outData)
            except queue.Empty:
                pass
        self.window.after(10, self.process_serial)  
        
    def return_key_pressed_seerial_port(self, event=None):   
       pass
                   
    def ava_seerial_temp(self, event=None):
        
        try:
            if self.yhenduseTextTemp.get() == "Katkesta temp.":
                self.yhenduseTextTemp.set("Ühenda temp.")
                self.thread.ser.close()
                self.thread.ser.flush()
                self.thread.stop()
            else:
                if event==None:
                    if not self.thread.ava_seerial(['COM19','9600']): # ava seerialyhendus
                        self.yhenduseTextTemp.set("Katkesta temp.")
                        self.thread.start() # käivitab seeriali lõime
                        if self.process_serial_called:
                            self.process_serial()
                            print("Käivitan process serial lõime")
                        self.clicked_on_leia_seerial_pordid()
                elif  self.valitud_seerial_port.get():
                    self.thread.ava_seerial([self.valitud_seerial_port.get(),'9600'])
                    self.yhenduseTextTemp.set("Katkesta temp.")
                else:
                    tk.messagebox.showinfo("Viga", "Ei õnnestunud temp. yhendamine") 
                    return
            print(self.keylogger.isAlive())
            if not self.keylogger.isAlive():
                print("Keylogger aktiveeritud")
                self.keylogger = keyboard.Listener(on_release=self.on_release)
                self.keylogger.start()
        except:
            pass
    def ava_seerial_sensor(self, event=None): 
        try:
            if self.yhenduseTextSensor.get() == "Katkesta sensor":
                self.yhenduseTextSensor.set("Ühenda sensor")
                self.thread2.ser.close()
                self.thread2.ser.flush()
                self.thread2.stop()
            else:
                if event==None:
                    if not self.thread2.ava_seerial(['COM20','4800']): # ava seerialyhendus
                        self.yhenduseTextSensor.set("Katkesta sensor")
                        self.thread2.start() # käivitab seeriali lõime
                        if self.process_serial_called:
                            self.process_serial()
                        self.clicked_on_leia_seerial_pordid()
                elif  self.valitud_seerial_port.get():
                    self.thread2.ava_seerial([self.valitud_seerial_port.get(),'4800'])
                    self.yhenduseTextSensor.set("Katkesta sensor")
                else:
                    tk.messagebox.showinfo("Viga", "Ei õnnestunud sensori yhendamine") 
                    return
                   
                
                self.process_serial()
            if not self.keylogger.isAlive():
                self.keylogger = keyboard.Listener(on_release=self.on_release)
                self.keylogger.start()
        except:
            pass
        

if __name__ == '__main__':
    
    root = tk.Tk()
    sensor = Smartsensor(root)
    root.lift ()
    root.lift()
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    root.focus_force()
    root.mainloop()
    
     
