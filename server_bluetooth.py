# -*- coding:Utf-8 -*-
'''
Created on 6 d�c. 2013

@author: Utilisateur
'''

import bluetooth

class Server_bluetooth:
    def __init__(self):
        
        
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
        
    def new_connexion(self):
        
       
        
        print "En attente de devices..."
        # accept incoming connections
        (client_sock, client_info) = self.server_socket.accept()
        self.client_sockets.append(client_sock)
        print "Accepted Connection from ", client_info
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
        
        print "all done"
        
    def display_msg(self, data):
        msg = []
        for i in range(len(data)):
            msg[i] = ord(data[i])
        print "Received : %x", msg
            
        
if __name__ == "__main__":
    bt_server =  Server_bluetooth()
    client_sock, client_info = bt_server.new_connexion()
    
    while True:
        data = bt_server.receive_data(client_sock)
        print(data)
        
    bt_server.disconnect()
