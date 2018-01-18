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
        outputparams = ['Kiirus','Pikkus','Pikkus //t kiirus', 'Sagedus', 'Kirje'] # siia panna võimalikud valikud väljundsuurustele
        
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()
        self.ser = ""    
        # 2: Load an ui file
        builder.add_from_file(os.path.dirname(os.path.realpath(__file__))+'\ELOVIS smartsensor.ui')

        # 3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('main_frame', master)
        master.title("Smartsensor v ")
        master.minsize(width=410, height=145)
        
        # 4: impordi pygubu's defineeritud muutujad
        self.kiirus= builder.get_variable("kiirus")
        self.pikkus = builder.get_variable("pikkus")

        self.seadmeseerial = serial.Serial()
        self.valitud_seerial_port = builder.get_variable("valitud_seerial_port")
        
        # 5: impordi pygubu's defineeritud objektid
        self.combobox_seerial_pordid = builder.get_object("combobox_seerial_pordid", master)
        self.yhenduseText = builder.get_variable("yhenduseText")
        self.keskmistamine = builder.get_variable("keskmistamine")
        self.kiirus_stdev = builder.get_variable("kiirus_stdev")
        self.statusText = builder.get_variable("status_text")
        self.sagedus = builder.get_variable("sagedus")
        self.StartStop = builder.get_variable("StartStop")
        self.hold = False
        #self.enableOutput = False
        
        self.valitud_output_parameter = builder.get_object("Combobox_output", master)
        self.valitud_output_parameter['values']=outputparams
        
        self.checkButtonOutput = builder.get_variable("checkButtonOutput")
        # 6 ühendab ui failis kirjeldatud tegevuste nimed funktsioonidega
        builder.connect_callbacks(self)

        self.window = master
        self.moisapi = False
        
        self.queue = queue.Queue()   
        self.thread = SerialThread(self.queue)
        self.thread.daemon = True
        self.kiirused = []
        self.pikkusStart=None
        self.pikkusStop=None
        self.process_serial()
        self.keylogger = threading.Thread()
        self.keylogger.daemon = True
        
    def on_release(self, key):
        '''
        Funktsioon arvutiga ühendatud seadmega suhtlemiseks:
        'F12' klahvi peale arvuti küsib seadmelt käsuga (kirjutatud vastavasse lahtrisse) andmed ja edastab aktiivsele aknale
        
        '''
        global shell
        try: k = key.char # single-char keys
        except: k = key.name # other keys
        if key == keyboard.Key.esc: return False # stop listener
        if k in ['f9']: # keys interested
            if self.checkButtonOutput.get():
                for case in switch(self.valitud_output_parameter.get()):
                    if case('Kiirus'):
                        shell.SendKeys(self.kiirus.get()+'~')
                        break
                    if case('Pikkus'):
                        shell.SendKeys(self.pikkus.get()+'~')
                        break
                    if case('Sagedus'):
                        shell.SendKeys(self.sagedus.get()+'~')
                        break
                    if case('Pikkus //t kiirus'):
                        shell.SendKeys(self.pikkus.get()+"\t"+self.kiirus.get()+'~')
                        break
                    if case('Kirje'):
                        shell.SendKeys(self.statusText.get()+'~')
                        break
                    if case(): # default, could also just omit condition or 'if True'
                        shell.SendKeys('\t'.join((self.statusText.get()).split(" "))+'~')
                        break
                winsound.MessageBeep()  
        
    def clickedOnHold(self): 
        self.hold = not self.hold
        
    def clicked_on_start_stop(self, event=None): 
        if not self.pikkusStart and not self.pikkusStop:
            self.pikkusStart=float(self.pikkus.get())
            self.StartStop.set("Stop")
        elif self.pikkusStart and not self.pikkusStop:
            self.pikkusStop=float(self.pikkus.get())
            messagebox.showinfo("Tulemus", '{:.2f}'.format(self.pikkusStop-self.pikkusStart))
            self.pikkusStart=None
            self.pikkusStop=None
            self.StartStop.set("Start")
            
        else:
            self.pikkusStart=None
            self.pikkusStop=None
            self.StartStop.set("Start")
            
        
    def clicked_on_leia_seerial_pordid(self, event=None):
        result = otsi_seerial()
        if result:
            self.combobox_seerial_pordid['values']=result
        else:
            tk.messagebox.showinfo("Viga", "Ei leidnud ühtegi vaba COM ühendust!\nKontrolli ühendusi!")

        
    def process_serial(self):
        while self.queue.qsize():
            try:
                kirje = self.queue.get().decode("utf-8").split(" ")
                #print(kirje)
                self.kiirused.append(float(kirje[2]))                
                if self.keskmistamine.get() != "" and int(self.keskmistamine.get()) > 1:
                    vahe = int(self.keskmistamine.get())-len(self.kiirused) # keskmistamise arvu ja listi pikkuse vahe
                    if vahe<0:
                        for i in range(0,-vahe): # kui keskmistamise number on v2iksem kui listis olevad arvud, siis kustutame vanad 2ra
                            self.kiirused.remove(self.kiirused[0]) # eemaldan viimase väärtuse
                    if vahe==1:
                       self.kiirused.remove(self.kiirused[0])
                else:
                    if len(self.kiirused) > 3:
                        self.kiirused.remove(self.kiirused[0])
                keskmine = 0
                max = 0
                min = 2400
                for kiirus in self.kiirused:
                    if len(self.kiirused)>1:
                        if kiirus>max:
                            max=kiirus
                        if kiirus<min:
                            min=kiirus
                    keskmine = keskmine + kiirus
                if not self.hold:
                    self.statusText.set((' '.join(kirje).replace("\n"," ")))
                    self.pikkus.set(float(kirje[1]))
                    self.kiirus_stdev.set('{:.2f}'.format(max-min))
                    self.kiirus.set('{:.2f}'.format(keskmine/len(self.kiirused))) 
                    self.sagedus.set('{:.5f}'.format(float(self.kiirus.get())/60))       
            except queue.Empty:
                pass
        self.window.after(10, self.process_serial)  
        
    def return_key_pressed_seerial_port(self, event=None):   
       pass
                   
    def ava_seerial(self, event=None):
        
        try:
            if self.yhenduseText.get() == "Katkesta":
                self.yhenduseText.set("Yhenda")
                self.thread.ser.close()
                self.thread.ser.flush()
                self.thread.stop()
            else:
                if event==None:
                    self.thread.ava_seerial(['COM18','57600'])
                    self.yhenduseText.set("Katkesta")
                elif  self.valitud_seerial_port.get():
                    self.thread.ava_seerial([self.valitud_seerial_port.get(),'57600'])
                    self.yhenduseText.set("Katkesta")
                else:
                    tk.messagebox.showinfo("Viga", "Ei õnnestunud") 
                    return
                self.thread.start() # käivitab seeriali lõime   
                self.process_serial()
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
    
     

