# -*- coding: utf-8 -*-
"""
Created on Tue May 27 14:54:24 2014

@author: Utilisateur
"""

import m_log as Log

import server_bluetooth



class Connexion_manager():
    def __init__(self, user_manager, debug = False):
        
        
        self.user_manager = user_manager
        
        self.debug = debug
        self.TAG = "Connexion_manager"
        Log.d(self.TAG, "Initialized", self.debug)
    
    
    def new_smartphone_user(self):
        Log.d(self.TAG, "Start new user connexion", self.debug)
        conn = _Smartphone_connexion(debug=True)
        client_info = conn.connect()
        self.user_manager.new_user(client_info, conn)
    

    
    
class mConnexion():
    def connect(self):
        pass
    
    def receive(self):
        pass
    
    def disconnect(self):
        pass
    
    
class _Wii_connexion_manager(mConnexion):
    pass


class _Smartphone_connexion(mConnexion):
    def __init__(self, debug = False):
        self.bt_server =  server_bluetooth.Server_bluetooth()
        
        self.debug = debug
        self.TAG = "_Smartphone_connexion"
        Log.d(self.TAG, "Initialized", self.debug)
        
    def connect(self):
        Log.d(self.TAG, "Waiting for connexion", self.debug)
        self.client_sock, self.client_info = self.bt_server.new_connexion()
        Log.d(self.TAG, "New connexion with %s"%(str(self.client_info)), self.debug)
        return self.client_info
        
    def receive(self):
        data = self.bt_server.receive_data(self.client_sock)
        return self._data_treatment(data)
        
    def _data_treatment(self, in_data):
        out_data = in_data.decode('utf-8')
        return out_data
        
    def disconnect(self):
        self.bt_server.disconnect()
        Log.d(self.TAG, "Disconnected", self.debug)