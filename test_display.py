# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 15:59:12 2014

@author: Utilisateur
"""


import time
import threading
import input_data_display

from multiprocessing import Queue
    
class Launcher(threading.Thread): 
    def __init__(self, queue): 
        threading.Thread.__init__(self)
        self.queue = queue
        self.values = [0, 0, 0, 0]
        self.colors = [1, 0, 1, 0]

        self.queue.put((self.values, self.colors))
        threading.Thread(None, launch_pyg, None, args = (self.queue, )).start()

    def run(self): 
        i = 0
        while True:
            time.sleep(1/50)
            self.values[0] = i%10
            self.values[1] = i%10  
            i +=1
            self.queue.put((self.values, self.colors))

class Pyg(threading.Thread): 
    def __init__(self, queue, name = 'bla'): 
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue

    def run(self): 
        input_data_display.Signal_Monitor(self.queue, 500, 900).start()

def launch_pyg(queue): 
    pyg = Pyg(queue, "hi")
    pyg.start()
    
if __name__ == "__main__":
    
    Launcher(Queue()).start()
    
    
    
    
    