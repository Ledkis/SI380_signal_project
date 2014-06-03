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

# Space between for the information for log
SPACE = 15
# Length of the buffer witch contains the accelerometers values
BUFF_LEN = 5
# Length of the mouvment state buffer 
STATE_BUFF_LEN = 10
# Seuil under witch we say there is no movement
GESTURE_SEUIL = 0.8
# Min number of consecutive 1 mouvment state for switching in gesture mode
MIN_GESTURE_DETECTION_SEUIL = 5
# Min number of consecutive -1 mouvment state for switching in not gesture mode
MIN_NO_GESTURE_DETECTION_SEUIL = 5

class User_manager():
    """Class for managing users.
    """
    def __init__(self, gesture_database_manager, debug = False):
        
        self.gesture_database_manager = gesture_database_manager
        
        self.user_list = []
        
        # Pygame object for ploting incoming accelerometer values
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
        self.continuous_mode = False
        
        # Represent if the user is working or not
        self.done = False
        
        self.debug = True
        self.TAG = "User %s"%(self.name)
        Log.d(self.TAG, "New user : %s"%self.name, self.debug)
        
        
    def run(self):
        
        
        # Buffer witch contains the last BUFF_LEN accelerometer values
        self.acc_buff = np.zeros((3, BUFF_LEN))
        # List witch contains the accelerometer values of the gesture currently performed gesture
        self.gesture = []
        # List witch contains the list of gesture associated to a new gesture
        # in apprentissage mode
        self.gesture_list = []
        # Buffer witch contains the last STATE_BUFF_LEN mouvment state
        self.mouvment_state_buff = np.zeros((1, STATE_BUFF_LEN))
        
        # Reference to the accelerometer value x, y, z. The last one represent
        # if we are in gesture mode or not (we use this for adapting the color
        # of the dot in the monitor)
        self.acc_values  = [0, 0, 0, 0]
        
        # We give the reference of the accelerometer values to the monitor
        self.manager.monitor.init_data_ref(self.acc_values)
        self.manager.monitor.start()
        
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
                        Log.d(self.TAG, "[ERROR] data not complete : %s"%(data), self.debug)
                except:
                    Log.d(self.TAG, "[ERROR] While _acc_treatment : %s"%(sys.exc_info()[0]), self.debug)
                    traceback.print_exc()
                    return
                 
                 
                if self.continuous_mode:
                    self.eval_gesture_state()
                    if self.gesture_mode:
                        self.gesture.append(self.acc_values)
                    
                else:
                    self.gesture.append(self.acc_values)
                    self.acc_values[3] = 1 #Red
                    #self._display_acc(self.acc_values, "[%s]"%msg)
                
            # When we switch in apprentissage mode
            if msg == "start_app":
               self.app_mode = True
               Log.d(self.TAG, "Start apprentissage", self.debug)
            
            # When we quit apprentissage mode
            if msg == "end_app":
                
                gesture_name = data[1]
                
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
                # We start a nex gesture recongnition with the current gesture
                self.gesture_database_manager.gesture_recognition(self.gesture)
                # we clear the accelerometer values in the gesture
                self.gesture = []
                Log.d(self.TAG, "End Continuous mode", self.debug)
            
            # When we stop to receive acceleromter data
            if msg == "end_data":
                self.acc_values[3] = 0 #Black
                Log.d(self.TAG, "End data", self.debug)
                # We tcheck if we where in app mode or not
                if self.app_mode:
                    self.gesture_list.append(self.gesture)
                else:
                    self.gesture_database_manager.gesture_recognition(self.gesture)
                # We don't forget to clear the current gesture
                self.gesture = []
                
    
    def eval_gesture_state(self, strong = True):
        self.update_acc_buff(self.acc_values[0:3])
        state = self._tcheck_mouvment()
        if strong:        
        
            self.update_mouvment_state_buff(state)
            if self.gesture_mode:
                no_move_length = np.sum(self.mouvment_state_buff[:,-MIN_NO_GESTURE_DETECTION_SEUIL:])
                no_gesture_cond = (no_move_length == -MIN_NO_GESTURE_DETECTION_SEUIL)
                if no_gesture_cond:
                    self.set_gesture_mode(False)
                    self.acc_values[3] = 0 #Black
                            
            else:
                move_length = np.sum(self.mouvment_state_buff[:,-MIN_GESTURE_DETECTION_SEUIL:])
                gesture_cond = (move_length == MIN_GESTURE_DETECTION_SEUIL)
                if gesture_cond:
                    self.set_gesture_mode(True)
                    # We add the acceleration values used to switch in gesture mode
                    for i in range(MIN_GESTURE_DETECTION_SEUIL):
                        acc = self.acc_buff[:, BUFF_LEN-MIN_GESTURE_DETECTION_SEUIL+i -1]
                        self.gesture.append(acc)
                    self.acc_values[3] = 1 #Red
                    
                    #TODO : Creat a function to color the MIN_GESTURE_DETECTION_SEUIL
                    # points who used for the swich in gesture mode
            
        else:
            self.set_gesture_mode(state == 1)
            
    def set_gesture_mode(self, mode):
        """Called when a new change of gesture mode is detected
        """
        self.gesture_mode = mode
        
        if not self.gesture_mode:
            self.gesture_database_manager.gesture_recognition(self.gesture)
            self.gesture = []

            
    def update_acc_buff(self, acc_values):
        """Update the acc_buff we the new acceleration.
        """
        for i in range(1, BUFF_LEN):
            self.acc_buff[:, i-1] = self.acc_buff[:, i]
            
        self.acc_buff[:, BUFF_LEN-1] = acc_values
    
    def update_mouvment_state_buff(self, state):
        """Update the mouvment_state_buff we the new state.
        """
        for i in range(1, STATE_BUFF_LEN):
            self.mouvment_state_buff[:, i-1] = self.mouvment_state_buff[:, i]
            
        self.mouvment_state_buff[:, STATE_BUFF_LEN-1] = state
        
        #Log.d(self.TAG, "mouvment_state_buff : %s"%str(self.mouvment_state_buff), self.debug)
        

    def _tcheck_mouvment(self):
        """ We tcheck if there is a mouvment : 
        1 -> mouvment detected
        -1 -> no mouvment detected
        
        A mouvment is detected if a the same time all the x, y & z acceleration 
        are above the GESTURE_SEUIL
        """
        
        t_x = np.abs(np.mean(self.acc_buff[0, 0:-1]) - self.acc_buff[0,-1]) < GESTURE_SEUIL
        t_y = np.abs(np.mean(self.acc_buff[1, 0:-1]) - self.acc_buff[1,-1]) < GESTURE_SEUIL
        t_z = np.abs(np.mean(self.acc_buff[2, 0:-1]) - self.acc_buff[2,-1]) < GESTURE_SEUIL
        
        if t_x and t_y and t_z:
            # No mouvment is detected
            return -1 
        else:
            # A mouvment is detected
            return 1
            
        
    def _acc_treatment(self, data):
        """ We make sure the accelerometer values are in the good format
        """
        x, y, z = data
        x, y, z, = float(x), float(y), float(z)
        return (x, y, z)
            
    
    def _display_acc(self, acc_values, mode = ""):
        Log.d(self.TAG, "%s%s"%(mode.ljust(SPACE), "".join([str(i).ljust(SPACE) for i in acc_values])), self.debug)
            
        
    def stop(self):
        self.done = True
        Log.d(self.TAG, "Stop", self.debug)