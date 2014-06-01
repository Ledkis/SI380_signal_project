# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 21:50:40 2014

@author: Utilisateur
"""

import m_log as Log

import threading
import pygame


BACKGROUND_COLOR = (255, 255, 255)
X_POINT_COLOR = (0, 0, 0)
Y_POINT_COLOR = (0, 0, 0)
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
            x = self.values[0]
            y = self.values[1]
            z = self.values[2]
            self.monitor.draw(x, y, z)
        
class Signal_Display():
    def __init__(self, monitor, width_px, height_px, debug = True):
        
        
        self.monitor = monitor
        
        self.width = width_px
        self.height = height_px
        
        self.x_vals = [0]*self.width
        self.y_vals = [0]*self.width
        self.z_vals = [0]*self.width
        
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
        
        
    def update_data(self, x, y, z):
        
        for i in range(1, self.width):
            self.x_vals[i-1] = self.x_vals[i]
            self.y_vals[i-1] = self.y_vals[i]
            self.z_vals[i-1] = self.z_vals[i]
          
          
        self.x_vals[-1] = self.remap(x)
        self.y_vals[-1] = self.remap(y)
        self.z_vals[-1] = self.remap(z)
        
    def remap(self, val):
        return int(m_map(val, MIN_VAL, MAX_VAL, self.max_height, -self.max_height))
          
        
    def draw(self, x, y, z):
        
        if not self.monitor.done:
        
            self.surface.fill(BACKGROUND_COLOR)
            
            for event in pygame.event.get():
                print(event)
                if (event.type == pygame.QUIT):
                    self.monitor.done = True
            
           
            self.update_data(x, y, z)
           
            for i in range(self.width):
                #x data
                x_acc_pos = (i, self.x_ord + self.x_vals[i])
                pygame.draw.circle(self.surface, X_POINT_COLOR, x_acc_pos, POINT_RADIUS, POINT_WIDTH)       
                #y data
                y_acc_pos = (i, self.y_ord + self.y_vals[i])
                pygame.draw.circle(self.surface, Y_POINT_COLOR, y_acc_pos, POINT_RADIUS,  POINT_WIDTH)       
                #z data
                z_acc_pos = (i, self.z_ord + self.z_vals[i])
                pygame.draw.circle(self.surface, Z_POINT_COLOR, z_acc_pos, POINT_RADIUS, POINT_WIDTH)
    
            pygame.display.flip()
            
def m_map(x, current_min, current_max, target_min, target_max):
    return ((target_max-target_min)/(current_max-current_min))*x+((current_min*target_max-target_min*current_max)/(current_min-current_max))  
            
if __name__ == "__main__":
    
    monitor = Signal_Monitor(500, 100)
    values = [0, 0, 0]    
    monitor.init_data_ref(values)
    monitor.start()
    
    
    i = 0
    while True:
        values[0] = i%10
        values[1] = i%10  
        
        i +=1
       