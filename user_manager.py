# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:40:24 2014

@author: Utilisateur
"""

import m_log as Log
from input_data_display import Signal_Monitor
import m_buffer
import m_treatment

import sys
import time
import traceback
import threading
'''
# cvKmeans module help to recognition optimazation Indeed 
# instead of going through each element of the dictionary
import cvKMeans '''
from multiprocessing import Queue

import numpy as np

G_CONST = 9.81

# Space between for the information for log
SPACE = 15

class User_manager():
    """Class for managing users.
    """
    def __init__(self, gesture_database_manager, debug = False):
        
        self.gesture_database_manager = gesture_database_manager
        
        self.acc_treatment = m_treatment.Data_Treatment()

        self.user_list = []
        
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
    """Represent a User.
    A user is a thread which receive data from its connexion and perform
    treatment on it (such as gesture recognition)
    """
    def __init__(self, name, connexion, user_manager, debug = True):
        threading.Thread.__init__(self) 
        self.manager = user_manager
        self.name = str(name)
        
        # Connexion object from witch the user receive the incoming data
        self.connexion = connexion
        
        self.gesture_database_manager = user_manager.gesture_database_manager
        
        # Represent if a gesture is currently being performed or not
        self.gesture_mode = False
        # Represent if the user is in the apprentissage mode or not
            # The apprentissage mode is when we teach new gesture to the application
        self.app_mode = False
        # Reprensent if the user is in the continuous mode or not
            # The continuous mode is when the application guess by itself if
            # a gesture is currently being performed or not. It's not the user
            # who say anymore if he perform a gesture or not
        self.continuous_mode = True
        
        # Represent if the user is working or not
        self.done = False
        
        # Pygame object for ploting incoming accelerometer values
        self.queue = Queue()
        
#        launcher = lambda queue : User_Signal_Monitor(queue, user_name="user monitor").start()
#        threading.Thread(None, launcher, None, args = (self.queue, )).start()
        
        User_Signal_Monitor(self.queue).start()

        self.debug = True
        self.TAG = "User %s"%(self.name)
        Log.d(self.TAG, "New user : %s"%self.name, self.debug)
        
        
    def run(self):
        
        
        # List witch contains the accelerometer values of the gesture currently performed gesture
        self.gesture = []
        # List witch contains the list of gesture associated to a new gesture
        # in apprentissage mode
        self.gesture_list = []
        
        # Reference to the accelerometer value x, y, z
        self.acc_values  = [0, 0, 0]
        
        # represent the different signals we want to display
        self.sig_val = []
        # Represent the color of the displayed signals.
        self.sig_colors  = []
        
        import test_display
        test_display.launch_pyg(self.queue)
        
        time.clock()
        Log.d(self.TAG, "Start loop", self.debug)
        while not self.done:
            try:
                # Data reception
                data = self.connexion.receive()
            except:
                Log.d(self.TAG, "[ERROR] While receiving : %s"%(sys.exc_info()[0]), self.debug)
                traceback.print_exc()
            try:
                # Data Treatment
                self._data_treatment(data)
            except:
                Log.d(self.TAG, "[ERROR] While _data_treatment : %s"%(sys.exc_info()[0]), self.debug)
                traceback.print_exc()
               
        Log.d(self.TAG, "End run", self.debug)
            
                
    def _data_treatment(self, in_data):
        
        # Sometimes we get more than one message in the socket buffer
        # so we make sure to treat the message independently
        data_list = in_data.split("\n")
        
        for data in data_list:
            # Each information in the incoming are separated by the ";" character
            data = data.split(";")
            # the type of message is always the header
            msg = data[0]
            
            # When we receive accelerometer values
            if msg == "gesture" or msg == "app":
                try:
                    if len(data[1:]) == 3: #TODO : Can be better (by improving the messages)
                        x, y, z = self._acc_treatment(data[1:])
                        # We update the value of acceleration
                        self.acc_values[0] = x
                        self.acc_values[1] = y
                        self.acc_values[2] = z
                    else :
                        Log.d(self.TAG, "[ERROR] data not complete : %s"%(data), False)
                except:
                    Log.d(self.TAG, "[ERROR] While _acc_treatment : %s"%(sys.exc_info()[0]), False)
                    #traceback.print_exc()
                    return
                 
                if self.continuous_mode:
                    self.continuous_recognition()
                        
                else:
                    self.gesture.append(self.acc_values)
                    self.sig_val = self.acc_values
                    self.sig_colors = [1]*3 #Red
                    self.queue.put((self.sig_val, self.sig_colors))                    
                                        
            # When we switch in apprentissage mode
            if msg == "start_app":
               self.app_mode = True
               Log.d(self.TAG, "Start apprentissage", self.debug)
            
            # When we quit apprentissage mode
            if msg == "end_app":
                
                gesture_name = data[1].strip().lower()
                
                # We add a new gesture in the gesture data base
                self.gesture_database_manager.new_gesture(gesture_name, self.gesture_list)
                # we clear the accelerometer values in the gesture                
                self.gesture = []
                # We clear the gestures
                self.gesture_list = []
                
                

                self.app_mode = False
                Log.d(self.TAG, "Fin apprentissage, gesture name = %s"%gesture_name, self.debug)
                
            # When we switch in continuous mode
            if msg == "start_continuous":
                self.continuous_mode = True
                Log.d(self.TAG, "Start Continuous mode", self.debug)
            
            # When we quit continuous mode
            if msg == "end_continuous":
                self.continuous_mode = False
                # we clear the accelerometer values in the gesture
                self.gesture = []
                Log.d(self.TAG, "End Continuous mode", self.debug)
            
            # When we stop to receive acceleromter data
            if msg == "end_data":
                self.sig_colors = [0]*3 #Black
                Log.d(self.TAG, "End data", self.debug)
                
                # We don't forget to clear the current gesture
                self.gesture = []
                # We clear the queue
                while not self.queue.empty():
                    self.queue.get()
                
    
    def continuous_recognition(self):
        
        self.gesture = self.manager.acc_treatment.perform(self.acc_values,
                                                          continuous = True,
                                                          queue = self.queue)
        
        if self.gesture is not None:
            m_teta, g_proj = self.gesture[0]
            Log.d(self.TAG, "New user gesture:\nm_teta = %s; m_g_proj = %s"%(m_teta, g_proj), True)
            
            if self.app_mode:
                self.gesture_list.append(self.gesture)
            else:
                self.gesture_database_manager.gesture_recognition(np.array(self.gesture[1:]))
                
    def _acc_treatment(self, data):
        """ We make sure the accelerometer values are in the good format
        """
        x, y, z = data
        x, y, z, = float(x), float(y), float(z)
        return (x, y, z)
            
    
    def stop(self):
        self.done = True
        Log.d(self.TAG, "Stop", self.debug)
        
class User_Signal_Monitor(threading.Thread): 
    def __init__(self, queue, user_name = 'bla'): 
        threading.Thread.__init__(self)
        self.user_name = user_name
        self.queue = queue

    def run(self): 
        Signal_Monitor(self.queue, 500, 900, title = self.user_name).start()