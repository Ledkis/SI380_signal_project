# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:20:32 2014

@author: Utilisateur
"""

import dtw

import m_log as Log

import numpy as np
import threading

import os

PATH = "gesture_data_base/"
FILE_NAME = "gesture_data_base.txt"

GESTURE_DELIMITER = "============================="
GESTURE_LIST_DELIMITER = "---------------------------"
ACC_DELIMITER = "||"

LJUST = 15

class Gesture_database_manager():
    def __init__(self, path, debug = False):
        self.path = path
        
        self.debug = debug
        self.TAG = "Gesture_database_manager"
        Log.d(self.TAG, "Initialized", self.debug)
        
        self.proto = []
        self.protolabels = []
        self.meta_data = []
        
        self.init_from_file()
        #self.tcheck_database()
        
        self.last_gesture_name = None
        
        
    def new_gesture(self, gesture_name, gesture_list):
        """
        
        TODO : Brut force
        """
        
        if len(gesture_list) == 0 :
                Log.d(self.TAG, "The new gesture '%s' contain no data -> not saved"%gesture_name, self.debug)
                return
        
        for gesture in gesture_list:
            g_meta_data = gesture[0]
            gesture = np.array(gesture[1:])
            
            self.meta_data.append(g_meta_data)
            self.proto.append(gesture)
            self.protolabels.append(gesture_name)
            
        
        #self.display_database()
        Log.d(self.TAG, "Nouveau geste appris : %s"%(gesture_name), self.debug)
        
        self.save()
        
    def __str__(self):
        s = ""
        for i in range(len(self.proto)):
            g_name = self.protolabels[i]
            g = self.proto[i]
            s += self.gesture_to_string(g_name, g)
        return s
        
    def gesture_to_string(self, g_name, gesture):
        return "%s\n%s\n"%(g_name, self.g_acc_to_string(gesture))
        
    def g_acc_to_string(self, gesture):
        gesture = gesture.T
        return "\n".join([";".join([str(acc) for acc in v_acc]) for v_acc in gesture])
        
    def save(self):
        file = open(PATH+FILE_NAME, "w")
        file.write(str(self))
        file.close()
        
        for i in range(len(self.proto)):
            g_name = self.protolabels[i]
            g = self.proto[i]
            file = open(PATH+g_name+".txt", "w")
            file.write(self.gesture_to_string(g_name, g))
            file.close()
        
        Log.d(self.TAG, "Data base saved", self.debug)
        
    def init_from_file(self):
        def to_float_list(l):
            return np.array([float(i) for i in l])        
        
        for file_name in os.listdir(PATH):
            if file_name != FILE_NAME:
                self.protolabels.append(file_name)
                file = open(PATH+file_name, "r").read().split("\n")[:-1]
                a_x = to_float_list(file[1].split(";"))
                a_y = to_float_list(file[2].split(";"))
                a_z = to_float_list(file[3].split(";"))
            
                gesture = np.array([a_x, a_y, a_z]).T
                self.proto.append(gesture)
                
            
#        def to_float_list(l):
#            return np.array([float(i) for i in l])        
#        
#        file = open(PATH+FILE_NAME, "r").read().split("\n")[:-1]
#        
#        l = int(len(file)/4)
#        
#        for i in range(0, l, 4):
#            self.protolabels.append(file[i])
#            
#            a_x = to_float_list(file[i+1].split(";"))
#            a_y = to_float_list(file[i+2].split(";"))
#            a_z = to_float_list(file[i+3].split(";"))
#            
#            gesture = np.array([a_x, a_y, a_z]).T
#            self.proto.append(gesture)
            
            
    def tcheck_database(self):
        """See if there is not appropriate gesture.
        """
        
        bad_gesture_list = []
        for gesture_name in self.gesture_dict.keys():
            ref_gesture = self.gesture_dict[gesture_name]
            
            if len(ref_gesture) ==0:
               bad_gesture_list.append(gesture_name)
               Log.d(self.TAG, "The gesture '%s' was not correct : empty"%gesture_name, self.debug) 
               continue
            
            for gesture in ref_gesture:
                
                x = gesture[0]
                y = gesture[1]
                z = gesture[2]
                
                if not (x.any() and y.any() and z.any()): #TODO : Not sure about that
                    bad_gesture_list.append(gesture_name)
                    Log.d(self.TAG, "The gesture '%s' was not correct : one of the gesture acc is empty"%gesture_name, self.debug)
                    break
                
        for gesture_name in bad_gesture_list:
            self.remove_gesture(gesture_name)
            
        self.save()
                    
    def remove_gesture(self, gesture_name):
        del self.gesture_dict[gesture_name]
        Log.d(self.TAG, "%s removed from gesture data base"%gesture_name, self.debug)
        
    def remove_all_gestures(self):
        self.gesture_dict.clear()
        Log.d(self.TAG, "All gestures removed from gesture data base", self.debug)
        
        
        
    def gesture_recognition(self, gesture):
        """
        Return None is problem
        """
        
        #TODO : review the good gesture condition
        if len(self.gesture_dict) == 0:
            Log.d(self.TAG, "No gesture in data base", self.debug)
            return
            
        if len(gesture) == 0:
           Log.d(self.TAG, "No data in gesture : ", self.debug)
           return 
            
        
        def perform_recognition(self, gesture_dict, gesture):
            gesture_name = dtw.multi_d_multi_key_dtw(gesture_dict, gesture)
            self._set_last_gesture_name(gesture_name)
            
        threading.Thread(None, perform_recognition, None, (self, self.gesture_dict, g), None).start()
        
        
    def _set_last_gesture_name(self, gesture_name):
        self.last_gesture_name = gesture_name
        Log.d(self.TAG, "New gesture recognized : %s"%self.last_gesture_name, self.debug)
        
    def print_gesture(self, gesture):
        s = ""
        for acc in gesture:
            s = "%s\n%s;"%(s,"".ljust(LJUST).join([str(a) for a in list(acc)]))
        print(s)
            