# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:20:32 2014

@author: Utilisateur
"""

import dtw

import m_log as Log

import numpy as np

PATH = "gesture_data_base/"
FILE_NAME = "gesture_data_base.txt"

GESTURE_DELIMITER = "============================="
GESTURE_LIST_DELIMITER = "---------------------------"
ACC_DELIMITER = "||"


class Gesture_database_manager():
    def __init__(self, path, debug = False):
        self.path = path
        
        self.debug = debug
        self.TAG = "Gesture_database_manager"
        Log.d(self.TAG, "Initialized", self.debug)
        
        self.gesture_dict = {}
        
        self.init_from_file()
        
        self.tcheck_database()
        
        
    def new_gesture(self, gesture_name, gesture_list):
        """
        
        TODO : Brut force
        """
        
        if len(gesture_list) == 0 :
                Log.d(self.TAG, "The new gesture '%s' contain no data -> not saved"%gesture_name, self.debug)
                return
        
        g_l = []
        
        for gesture in gesture_list:
            x_d = []            
            y_d = []            
            z_d = []
            
            for data in gesture:
                x_d.append(data[0])
                y_d.append(data[1])
                z_d.append(data[2])
                
            if not (x_d and y_d and z_d):
                Log.d(self.TAG, "One of the gesture acc is empty -> Gesture %s not saved"%gesture_name, self.debug)
                return
                
            x_d = np.array(x_d)
            y_d = np.array(y_d)
            z_d = np.array(z_d)
            g = np.array([x_d, y_d, z_d])
            
            g_l.append(g)
            
        g_l = np.array(g_l)
            
        self.gesture_dict[gesture_name] = g_l
        
        
        #self.display_database()
        Log.d(self.TAG, "Nouveau geste appris : %s"%(gesture_name), self.debug)
        
        self.save()
        
    def display_database(self):
        
        s = ""
        for gesture_name in self.gesture_dict.keys():
            s = "%s--- %s ---\n"%(s,gesture_name)
            for gesture in self.gesture_dict[gesture_name]:
                s = "%s%s\n"%(s,"--------------------")
                for acc_data in gesture:
                    for acc in acc_data:
                        s = "%s%s;"%(s,acc_data) 
                   
        Log.d(self.TAG, "Gesture data base :\n%s"%s, self.debug)
        
        
    def __str__(self):
        s = ""
        for gesture_name in self.gesture_dict.keys():
            s = "%s%s\n%s\n"%(s,GESTURE_DELIMITER,gesture_name)
            for gesture in self.gesture_dict[gesture_name]:
                s = "%s%s\n"%(s,GESTURE_LIST_DELIMITER)
                for acc_data in gesture:
                    for acc in acc_data:
                        s = "%s%s;"%(s,acc) 
                    s = "%s||\n"%s
        return s
        
    def save(self):
        file = open(PATH+FILE_NAME, "w")
        file.write(str(self))
        file.close()
        
        Log.d(self.TAG, "Data base saved", self.debug)
        
    def init_from_file(self):
        file = open(PATH+FILE_NAME, "r").read().replace("\n", "")
        
        gesture_list = file.split(GESTURE_DELIMITER)[1:]
        
        for gesture_info in gesture_list:
            gesture_info = gesture_info.split(GESTURE_LIST_DELIMITER)
            gesture_name = gesture_info[0]
            g_l = []
            for gesture_list in gesture_info[1:-1]:
                gesture = gesture_list.split(ACC_DELIMITER)

                def to_float_list(l):
                    return np.array([float(i) for i in l])
                
                x = to_float_list(gesture[0].split(";")[:-1])
                y = to_float_list(gesture[1].split(";")[:-1])
                z = to_float_list(gesture[2].split(";")[:-1])
                
                g = np.array([x, y, z])
                g_l.append(g)
            g_l = np.array(g_l)
            
            self.gesture_dict[gesture_name] = g_l
            
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
                
                if not (x and y and z):
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
        
        if len(self.gesture_dict) == 0:
            Log.d(self.TAG, "No gesture in data base", self.debug)
            return
        
        
        x_d = []            
        y_d = []            
        z_d = []
        
        for data in gesture:
            x_d.append(data[0])
            y_d.append(data[1])
            z_d.append(data[2])
            
        x_d = np.array(x_d)
        y_d = np.array(y_d)
        z_d = np.array(z_d)
        g = np.array([x_d, y_d, z_d])
        
        gesture_name = dtw.multi_d_multi_key_dtw(self.gesture_dict, g)
        
        Log.d(self.TAG, "New gesture recognized : %s"%gesture_name, self.debug)
        
        return gesture_name