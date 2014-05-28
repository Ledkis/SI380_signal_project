# -*- coding:Utf-8 -*-
'''
Created on 6 d�c. 2013

@author: Utilisateur
'''

import m_log as Log

import bluetooth
import datetime

class Server_bluetooth:
    def __init__(self, debug = False):
        
        
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.client_sockets = []
        self.uuid = "00001101-0000-1000-8000-00805F9B34FB"
       
        #On assigne une adresse à un numéro de port pour notre server socket
        self.server_socket.bind(("",bluetooth.PORT_ANY))
        self.port = self.server_socket.getsockname()[1]
        
        self.sockets = []
        
        # advertise service
        self.server_socket.listen(1)
        bluetooth.advertise_service(self.server_socket, "Validation Host",service_id = self.uuid, service_classes = [self.uuid, bluetooth.SERIAL_PORT_CLASS ], profiles = [ bluetooth.SERIAL_PORT_PROFILE ])
        
        self.debug = debug
        self.TAG = "Server_bluetooth"
        Log.d(self.TAG, "Initialized", self.debug)
        
    def new_connexion(self):
        
       
        
        Log.d(self.TAG, "En attente de devices...", self.debug)
        # accept incoming connections
        (client_sock, client_info) = self.server_socket.accept()
        self.client_sockets.append(client_sock)
        Log.d(self.TAG, "Accepted Connection from %s"%(str(client_info)), self.debug)
        self.sockets.append(client_sock)
        
        return (client_sock, client_info)
        
    def receive_data(self, client_sock):
        
        try:
            data = client_sock.recv(1024)
            return data
        except IOError:
            pass
        
    def disconnect(self):
        
        for client_sock in self.client_sockets :
            client_sock.close()
        
        self.server_socket.close()
        
        print("all done")
        
    def display_msg(self, data):
        msg = []
        for i in range(len(data)):
            msg[i] = ord(data[i])
        print("Received : %x", msg)
        
def save_data(data, file, path):
    data = data.decode('utf-8')
    data = data.split(";")
    if data[0] == "gce":
        
        x, y, z = data[1], data[2], data[3]
        print("gce : %s;%s;%s"%(x,y,z))
        file.write("%s;%s;%s\n"%(x, y, z))
    if data[0] =="bce":
        file.close()
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = path+"acc_data_"+now+".txt"
        print("bce, new file  : %s"%(file_name))
        file = open(file_name, "w")
            
        
if __name__ == "__main__":
    bt_server =  Server_bluetooth()
    client_sock, client_info = bt_server.new_connexion()
    path = "data/"
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file = open(path+"acc_data_"+now+".txt", "w")
    
    try:
        while True:
            data = bt_server.receive_data(client_sock)
            print(data)
            save_data(data, file, path)
    finally:
        file.close()
        
    bt_server.disconnect()
