# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 21:50:40 2014

@author: Utilisateur
"""

# TODO : to optimize with numpy

import m_log as Log


import threading
import numpy as np
import pygame

MAX_SIG = 10


BACKGROUND_COLOR = (255, 255, 255)

GESTURE_POINT_COLOR = (255, 0, 0)
NO_GESTURE_POINT_COLOR = (0, 0, 0)
Z_POINT_COLOR = (0, 0, 0)

MIN_VAL = -20
MAX_VAL = 20

POINT_RADIUS = 1
POINT_WIDTH = 0

FRAMERATE = 50

class Signal_Monitor(threading.Thread):
    def __init__(self, width_px, height_px):
        threading.Thread.__init__(self)
        pygame.init()
        
        self.monitor = Signal_Display(self, width_px, height_px)
        self.clock = pygame.time.Clock()
        self.done = False
        
    def init_ref(self, sig_val_ref, sig_color_ref):
        self.sig_val = sig_val_ref
        self.sig_color = sig_color_ref
        
    def run(self):
    
        while not self.done:
            self.clock.tick(FRAMERATE)
            self.monitor.draw(self.sig_val, self.sig_color)
        
class Signal_Display():
    def __init__(self, monitor, width_px, height_px, debug = True):
        
        
        self.monitor = monitor
        
        self.width = width_px
        self.height = height_px
        
        
        self.sig_val = np.zeros((MAX_SIG, self.width), dtype=int)
        
        self.max_height = self.height/6   
        self.x_ord = int(self.height/6)
        self.y_ord = 3*self.x_ord
        self.z_ord = 5*self.x_ord
        
        self.surface = pygame.display.set_mode((self.width, self.height))
        self.surface.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        
        
        
        self.debug = debug
        self.TAG = "Signal_Monitor"
        Log.d(self.TAG, "Initialized", self.debug)
        
        
    def update_data(self, sig_val):
        
        sig_size = len(sig_val)
         
        for i in range(1, self.width):
            self.sig_val[:, i-1] = self.sig_val[:, i]
        self.sig_val[:sig_size, -1] = self.remap_sig(sig_val)
        
    def remap_sig(self, sig_val):
        fmap = lambda val : int(m_map(val, MIN_VAL, MAX_VAL, -self.max_height, self.max_height))
        return [fmap(sig) for sig in sig_val]
          
    def eval_sig_ord(self, sig_nbr):
        max_height = self.height/(2*sig_nbr)
        return [int((2*i+1)*max_height) for i in range(sig_nbr)]        
            
        
    def draw(self, sig_val, sig_color):
        
        sig_nbr = len(sig_val)
        
        ord_list = self.eval_sig_ord(sig_nbr)
            
        
        
        if not self.monitor.done:
        
            self.surface.fill(BACKGROUND_COLOR)
            
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.monitor.done = True
            
           
            self.update_data(sig_val)
            
            for i in range(self.width):
                for s in range(sig_nbr):
                    c = sig_color[s]
                    if c == 0 :
                        c = NO_GESTURE_POINT_COLOR
                    elif c == 1 :
                        c = GESTURE_POINT_COLOR
                    sig_pos = (i, ord_list[s]+self.sig_val[s, i])
                    pygame.draw.circle(self.surface, c, sig_pos, POINT_RADIUS, POINT_WIDTH)       
    
            pygame.display.flip()
            
def m_map(x, current_min, current_max, target_min, target_max):
    return ((target_max-target_min)/(current_max-current_min))*x+((current_min*target_max-target_min*current_max)/(current_min-current_max))  
            
if __name__ == "__main__":
    
    monitor = Signal_Monitor(500, 200)
    values = [0, 0, 0, 0]
    colors = [1, 0, 1, 0]    
    monitor.init_ref(values, colors)
    monitor.start()
    
    
    i = 0
    while True:
        values[0] = i%10
        values[1] = i%10  
        
        i +=1
       