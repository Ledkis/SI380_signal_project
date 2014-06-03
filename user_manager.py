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

import numpy as np


SPACE = 15
BUFF_LEN = 5
GESTURE_SEUIL = 0.8
STATE_LEN = 10
MIN_GESTURE_DETECTION_SEUIL = 5
MIN_NO_GESTURE_DETECTION_SEUIL = 5

class User_manager():
    def __init__(self, gesture_database_manager, debug = False):
        
        self.gesture_database_manager = gesture_database_manager
        
        self.user_list = []
        
        self.monitor = input_data_display.Signal_Monitor(500, 500)
        
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
        
        self.gesture_mode = False
        self.app_mode = False
        self.continuous_mode = False
        
        self.done = False
        
        self.debug = True
        self.TAG = "User %s"%(self.name)
        Log.d(self.TAG, "New user : %s"%self.name, self.debug)
        
        
    def run(self):
        
        #TODO : Optimization with numpy instead python list
        self.buff = np.zeros((3, BUFF_LEN))
        self.gesture = []
        self.gesture_list = []
        self.gesture_state_list = np.zeros((1, STATE_LEN))
        
        self.acc_values  = [0, 0, 0, 0]
        
        self.manager.monitor.init_data_ref(self.acc_values)
        
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
                        x, y, z = self._acc_treatment(data[1:])
                        self.acc_values[0] = x
                        self.acc_values[1] = y
                        self.acc_values[2] = z
                    else :
                        Log.d(self.TAG, "[ERROR] data not complete : %s"%(data), self.debug)
                except:
                    Log.d(self.TAG, "[ERROR] While _acc_treatment : %s"%(sys.exc_info()[0]), self.debug)
                    traceback.print_exc()
                    return
                 
                 
                if self.continuous_mode:
                    self.eval_gesture_state(self.acc_values)
                    if self.gesture_mode:
                        self.gesture.append(self.acc_values)
                    
                else:
                    self.gesture.append(self.acc_values)
                    self.acc_values[3] = 1 #Red
                    #self._display_acc(self.acc_values, "[%s]"%msg)
                
            
            if msg == "start_app":
               self.app_mode = True
               Log.d(self.TAG, "Start apprentissage", self.debug)
            
            
            if msg == "end_app":
                
                gesture_name = data[1]
                
                self.gesture_database_manager.new_gesture(gesture_name, self.gesture_list)
                self.gesture = []
                self.gesture_list = []

                self.app_mode = False
                Log.d(self.TAG, "Fin apprentissage, gesture name = %s"%gesture_name, self.debug)
                
            if msg == "start_continuous":
                self.continuous_mode = True
                Log.d(self.TAG, "Start Continuous mode", self.debug)
            
            if msg == "end_continuous":
                self.continuous_mode = False
                self.gesture_database_manager.gesture_recognition(self.gesture)
                self.gesture = []
                Log.d(self.TAG, "End Continuous mode", self.debug)
            
            if msg == "end_data":
                self.acc_values[3] = 0 #Black
                Log.d(self.TAG, "End data", self.debug)
                if self.app_mode:
                    self.gesture_list.append(self.gesture)
                else:
                    self.gesture_database_manager.gesture_recognition(self.gesture)
                self.gesture = []
                
    
    def eval_gesture_state(self, acc_values, strong = True):
        self.update_buff(self.acc_values[0:3])
        state = self._tcheck_mouvment()
        if strong:        
        
            self.update_gesture_state_list(state)
            if self.gesture_mode:
                no_move_length = np.sum(self.gesture_state_list[:,-MIN_NO_GESTURE_DETECTION_SEUIL:])
                no_gesture_cond = (no_move_length == -MIN_NO_GESTURE_DETECTION_SEUIL)
                if no_gesture_cond:
                    self.set_gesture_mode(False)
                    self.acc_values[3] = 0 #Black
                            
            else:
                move_length = np.sum(self.gesture_state_list[:,-MIN_GESTURE_DETECTION_SEUIL:])
                gesture_cond = (move_length == MIN_GESTURE_DETECTION_SEUIL)
                if gesture_cond:
                    self.set_gesture_mode(True)
                    self.acc_values[3] = 1 #Red
            
        else:
            self.set_gesture_mode(state == 1)
            
    def set_gesture_mode(self, mode):
        self.gesture_mode = mode
        
        if not self.gesture_mode:
            self.gesture_database_manager.gesture_recognition(self.gesture)
            self.gesture = []

            
    def update_buff(self, acc_values):
        for i in range(1, BUFF_LEN):
            self.buff[:, i-1] = self.buff[:, i]
            
        self.buff[:, BUFF_LEN-1] = acc_values
    
    def update_gesture_state_list(self, state):
        for i in range(1, STATE_LEN):
            self.gesture_state_list[:, i-1] = self.gesture_state_list[:, i]
            
        self.gesture_state_list[:, STATE_LEN-1] = state
        
        #Log.d(self.TAG, "gesture_state_list : %s"%str(self.gesture_state_list), self.debug)
        

    def _tcheck_mouvment(self):
        t_x = np.abs(np.mean(self.buff[0, 0:-1]) - self.buff[0,-1]) < GESTURE_SEUIL
        t_y = np.abs(np.mean(self.buff[1, 0:-1]) - self.buff[1,-1]) < GESTURE_SEUIL
        t_z = np.abs(np.mean(self.buff[2, 0:-1]) - self.buff[2,-1]) < GESTURE_SEUIL
        
        x_mean = np.mean(self.buff[0, 0:-1])
        x = self.buff[0,-1]
        
        #Log.d(self.TAG, "x_mean = %s, x = %s"%(x_mean, x), self.debug) 
        
        if t_x and t_y and t_z:
            return -1 
        else:
            return 1
            
        
    def _acc_treatment(self, data):
        x, y, z = data
        x, y, z, = float(x), float(y), float(z)
        return (x, y, z)
            
    
    def _display_acc(self, acc_values, mode = ""):
        Log.d(self.TAG, "%s%s"%(mode.ljust(SPACE), "".join([str(i).ljust(SPACE) for i in acc_values])), self.debug)
            
        
    def stop(self):
        self.done = True
        Log.d(self.TAG, "Stop", self.debug)