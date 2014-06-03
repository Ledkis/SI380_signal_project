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
        
    def init_data_ref(self, data_ref):
        self.values = data_ref
        
    def run(self):
    
        while not self.done:
            self.clock.tick(FRAMERATE)
            self.monitor.draw(self.values)
        
class Signal_Display():
    def __init__(self, monitor, width_px, height_px, debug = True):
        
        
        self.monitor = monitor
        
        self.width = width_px
        self.height = height_px
        
        
        self.acc_val = np.zeros((4, self.width), dtype=int)
        
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
        
        
    def update_data(self, acc_val):
        
        for i in range(1, self.width):
            self.acc_val[:, i-1] = self.acc_val[:, i]
          
          
        self.acc_val[:, -1] = self.remap_acc(acc_val)
        
    def remap_acc(self, acc_val):
        fmap = lambda val : int(m_map(val, MIN_VAL, MAX_VAL, -self.max_height, self.max_height))
        return [fmap(acc) for acc in acc_val[0:3]]+[int(acc_val[3])]
          
        
    def draw(self, acc_val):
        
        if not self.monitor.done:
        
            self.surface.fill(BACKGROUND_COLOR)
            
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    self.monitor.done = True
            
           
            self.update_data(acc_val)
           
            for i in range(self.width):
                #Color:
                c = NO_GESTURE_POINT_COLOR
                c_val = self.acc_val[3, i]
                if c_val == 0:
                    c = NO_GESTURE_POINT_COLOR
                elif c_val ==1:
                    c = GESTURE_POINT_COLOR
                #x data
                x_acc_pos = (i, self.x_ord + self.acc_val[0, i])
                pygame.draw.circle(self.surface, c, x_acc_pos, POINT_RADIUS, POINT_WIDTH)       
                #y data
                y_acc_pos = (i, self.y_ord + self.acc_val[1, i])
                pygame.draw.circle(self.surface, c, y_acc_pos, POINT_RADIUS,  POINT_WIDTH)       
                #z data
                z_acc_pos = (i, self.z_ord + self.acc_val[2, i])
                pygame.draw.circle(self.surface, c, z_acc_pos, POINT_RADIUS, POINT_WIDTH)
    
            pygame.display.flip()
            
def m_map(x, current_min, current_max, target_min, target_max):
    return ((target_max-target_min)/(current_max-current_min))*x+((current_min*target_max-target_min*current_max)/(current_min-current_max))  
            
if __name__ == "__main__":
    
    monitor = Signal_Monitor(500, 100)
    values = [0, 0, 0, 1]    
    monitor.init_data_ref(values)
    monitor.start()
    
    
    i = 0
    while True:
        values[0] = i%10
        values[1] = i%10  
        
        i +=1
       