# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:38:12 2014

@author: Utilisateur
"""

import m_log as Log

import connexion_manager
import user_manager
import gesture_manager

data_base_path = "data/"

class Gesture_application():
    def __init__(self):
        
        #Initialization
        
        self.gesture_database_manager = \
        gesture_manager.Gesture_database_manager(data_base_path, \
                                                        debug = True)
                                                        
        self.user_manager = user_manager.User_manager(self.gesture_database_manager, 
                                                      debug=True)
        
        self.connexion_manager = \
        connexion_manager.Connexion_manager(self.user_manager, debug = True)
        
        #self.gesture_recognition
        
        Log.d(__name__, "Initialized", True)
        
        self.connexion_manager.new_smartphone_user()
        
        Log.d(__name__, "New user", True)
        
        self.user_manager.start_all_users()
        
        Log.d(__name__, "user started", True)
        
        
        
        
app = Gesture_application()