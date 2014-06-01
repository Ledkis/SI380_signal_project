# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:40:24 2014

@author: Utilisateur
"""

import m_log as Log
import input_data_display

import sys
import traceback
import threading


SPACE = 15

class User_manager():
    def __init__(self, gesture_database_manager, debug = False):
        
        self.gesture_database_manager = gesture_database_manager
        
        self.user_list = []
        
        self.monitor = input_data_display.Signal_Monitor(500, 900)
        
        self.debug = debug
        self.TAG = "User_manager"
        Log.d(self.TAG, "Initialized", self.debug)
        
        
    def new_user(self, name, connexion):
        self.user_list.append(User(name, connexion, self))
        
    def start_user(self, user_name):
        for user in self.user_list:
            if user.name == user_name:
                user.start()
                
    def start_all_users(self):
        for user in self.user_list:
            user.start()
            
    def stop_all_users(self):
        for user in self.user_list:
            user.stop()
        
    def stop_user(self, user_name):
        for user in self.user_list:
            if user.name == user_name:
                user.start()


class User(threading.Thread):
    def __init__(self, name, connexion, user_manager, debug = True):
        threading.Thread.__init__(self) 
        self.manager = user_manager
        self.name = str(name)
        self.connexion = connexion
        self.gesture_database_manager = user_manager.gesture_database_manager
        
        self.app_mode = False
        
        self.done = False
        
        self.debug = True
        self.TAG = "User %s"%(self.name)
        Log.d(self.TAG, "New user : %s"%self.name, self.debug)
        
        
    def run(self):
        
        self.gesture = []
        self.gesture_list = []
        
        self.values  = [0, 0, 0]
        
        self.manager.monitor.init_data_ref(self.values)
        
        self.manager.monitor.start()
        
        while not self.done:
            try:
                data = self.connexion.receive()
            except:
                Log.d(self.TAG, "[ERROR] While receiving : %s"%(sys.exc_info()[0]), self.debug)
                traceback.print_exc()
            try:
                self._data_treatment(data)
            except:
                Log.d(self.TAG, "[ERROR] While _data_treatment : %s"%(sys.exc_info()[0]), self.debug)
                traceback.print_exc()
               
        Log.d(self.TAG, "End run", self.debug)
               
            
                
    def _data_treatment(self, in_data):
        
        data_list = in_data.split("\n")
        
        for data in data_list:
            data = data.split(";")
            msg = data[0]
            
            if msg == "gesture" or msg == "app":
                try:
                    if len(data[1:]) == 3: #TODO : Can be better (by improving the messages)
                        self.x, self.y, self.z = self._acc_treatment(data[1:])
                        self.values[0] = self.x
                        self.values[1] = self.y
                        self.values[2] = self.z
                    else :
                        Log.d(self.TAG, "[ERROR] data not complete : %s"%(data), self.debug)
                except:
                    Log.d(self.TAG, "[ERROR] While _acc_treatment : %s"%(sys.exc_info()[0]), self.debug)
                    traceback.print_exc()
                    return
                self.gesture.append((self.x, self.y, self.z))
                self._display_acc(self.x, self.y, self.z, "[%s]"%msg)
                
            if msg == "start_app":
               self.app_mode = True
               Log.d(self.TAG, "Start apprentissage", self.debug)
            
            if msg == "end_app":
                
                gesture_name = data[1]
                
                self.gesture_database_manager.new_gesture(gesture_name, self.gesture_list)
                self.gesture = []
                self.gesture_list = []

                self.app_mode = False
                Log.d(self.TAG, "Fin apprentissage", self.debug)
                
            if msg == "end_data":
                Log.d(self.TAG, "End data", self.debug)
                if self.app_mode:
                    self.gesture_list.append(self.gesture)
                else:
                    self.gesture_database_manager.gesture_recognition(self.gesture)
                self.gesture = []
                
                
                
    def _acc_treatment(self, data):
        x, y, z = data
        x, y, z, = float(x), float(y), float(z)
        return (x, y, z)
            
    
    def _display_acc(self, x, y, z, mode = ""):
        Log.d(self.TAG, "%s%s %s %s"%(mode.ljust(SPACE), str(x).ljust(SPACE), 
                                                       str(y).ljust(SPACE), 
                                                       str(z).ljust(SPACE)),
                                                       self.debug)
            
        
    def stop(self):
        self.done = True
        Log.d(self.TAG, "Stop", self.debug)
                
    
        