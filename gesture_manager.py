# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:20:32 2014

@author: Utilisateur
"""

import cvKNN
import midiManager

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

gesture_to_midi_hm = {'lf' : 60,
                      'rf' : 61, 
                      'g' : 62, 
                      'r' : 63}                      
MIDI_OFFSET = 64

class Gesture_database_manager():
    def __init__(self, path, debug = False):
        self.path = path
        
        self.debug = debug
        self.TAG = "Gesture_database_manager"
        Log.d(self.TAG, "Initialized", self.debug)
        
        self.proto = []
        self.protoclass = []
        self.meta_data = []
        
        self.k = 3
#        self.centroide = init()
#        self.cluster = init()
        self.init_from_file()
        
        #TODO : Temporaire, revoir cette architecture
        self.midi_manager = midiManager.MidiManager()
        self.update_midi_gesture_mapping()
        
        self.last_gesture_name = None
        
    def update_midi_gesture_mapping(self):
        g_name_list = sorted(set(self.protoclass))
        for i in range(len(g_name_list)):
            gesture_to_midi_hm[g_name_list[i]] = MIDI_OFFSET + i
            
        
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
            self.protoclass.append(gesture_name)
            
            nbr = len(list(filter(lambda name : name.split("_")[0] == gesture_name, os.listdir(PATH))))+1
            file = open(PATH+gesture_name+"_"+str(nbr)+".txt", "w")
            file.write(self.gesture_to_string(gesture_name, gesture))
            file.close()
            
        self.update_midi_gesture_mapping()
            
        
        Log.d(self.TAG, "Nouveau geste appris et sauvé : %s\nProto nbr = %s"%(gesture_name, len(self.proto)), self.debug)
        
        self.save()
        
    def __str__(self):
        s = ""
        for i in range(len(self.proto)):
            g_name = self.protoclass[i]
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
        
        Log.d(self.TAG, "Data base saved", self.debug)
        
    def init_from_file(self):
        def to_float_list(l):
            return np.array([float(i) for i in l])        
        
        for file_name in os.listdir(PATH):
            if file_name != FILE_NAME:
                file = open(PATH+file_name, "r").read().split("\n")[:-1]
                self.protoclass.append(file[0])
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
#            self.protoclass.append(file[i])
#            
#            a_x = to_float_list(file[i+1].split(";"))
#            a_y = to_float_list(file[i+2].split(";"))
#            a_z = to_float_list(file[i+3].split(";"))
#            
#            gesture = np.array([a_x, a_y, a_z]).T
#            self.proto.append(gesture)
            
    def remove_all_gestures(self):
        self.proto = []
        self.protoclass = []
        Log.d(self.TAG, "All gestures removed from gesture data base", self.debug)
        
        
        
    def gesture_recognition(self, gesture):
        """
        Return None is problem
        """
        
        #TODO : review the good gesture condition
        if len(self.proto) == 0:
            Log.d(self.TAG, "No gesture in data base", self.debug)
            return
            
        if len(gesture) == 0:
           Log.d(self.TAG, "No data in gesture : ", self.debug)
           return 
            
        
        def perform_recognition(self, gesture, proto, protoclass, k):
            gesture_name = cvKNN.K_NN(gesture, proto, protoclass, k)
            midi_note = gesture_to_midi_hm[gesture_name]
            self.midi_manager.midiConnexion.send_Note_On(note = midi_note)
            self.midi_manager.midiConnexion.send_Note_Off(note = midi_note)
            self._set_last_gesture_name(gesture_name)
            
        threading.Thread(None, perform_recognition, None, (self, gesture, self.proto, self.protoclass, self.k), None).start()
        
        
    def _set_last_gesture_name(self, gesture_name):
        self.last_gesture_name = gesture_name
        Log.d(self.TAG, "New gesture recognized : %s"%self.last_gesture_name, self.debug)
        
    def print_gesture(self, gesture):
        s = ""
        for acc in gesture:
            s = "%s\n%s;"%(s,"".ljust(LJUST).join([str(a) for a in list(acc)]))
        print(s)
            