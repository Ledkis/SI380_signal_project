# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 21:50:40 2014

@author: Utilisateur
"""

# TODO : to optimize with numpy

import m_log as Log


from multiprocessing import Process, Queue, TimeoutError
import numpy as np
import pygame
import pygame.locals

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

class Signal_Monitor(Process):
    def __init__(self, width_px, height_px, title = None):
        super(Signal_Monitor, self).__init__()
        self.title = title
        self.width_px, self.height_px = width_px, height_px
        
    def init_queue(self, queue):
        self.queue = queue
        
    def run(self):
        
        pygame.init()
        
        self.surface = pygame.display.set_mode((self.width_px, self.height_px), pygame.locals.RESIZABLE)
        if self.title is not None:
            pygame.display.set_caption(self.title)
        self.surface.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        
        self.clock = pygame.time.Clock()
        self.done = False
        
        self.monitor = Signal_Display(self)
    
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    self.done = True
                    break
                if event.type == pygame.locals.VIDEORESIZE:
                    self.width_px, self.height_px = event.size
                    self.surface = pygame.display.set_mode((self.width_px, self.height_px),
                                                           pygame.locals.RESIZABLE)
            try:            
                sig_val, sig_color = self.queue.get(1/FRAMERATE)
                self.surface.fill(BACKGROUND_COLOR)
                self.monitor.draw(sig_val, sig_color)
                pygame.display.flip()                
                
            except TimeoutError:
                pass
            
        pygame.quit()
        
class Signal_Display():
    def __init__(self, monitor, debug = True):
        self.monitor = monitor
        
        self.sig_val = np.zeros((MAX_SIG, self.monitor.width_px), dtype=int)
        
        self.debug = debug
        self.TAG = "Signal_Monitor"
        Log.d(self.TAG, "Initialized", self.debug)
        
        
    def update_data(self, sig_val):
        sig_size = len(sig_val)
         
        for i in range(1, self.monitor.width_px):
            self.sig_val[:, i-1] = self.sig_val[:, i]
        self.sig_val[:sig_size, -1] = self.remap_sig(sig_val)
        
    def remap_sig(self, sig_val):
        fmap = lambda val : int(m_map(val, MIN_VAL, MAX_VAL, -self.max_height, self.max_height))
        return [fmap(sig) for sig in sig_val]
          
    def eval_sig_ord(self, sig_nbr):
        self.max_height = self.monitor.height_px/(2*sig_nbr)
        return [int((2*i+1)*self.max_height) for i in range(sig_nbr)]        
        
    def draw(self, sig_val, sig_color):
        sig_nbr = len(sig_val)
        
        if sig_nbr == 0:
            Log.d(self.TAG, "No signal to display", self.debug)
            return
        
        ord_list = self.eval_sig_ord(sig_nbr)
        
        if not self.monitor.done:
            self.update_data(sig_val)
            
            for i in range(self.monitor.width_px):
                for s in range(sig_nbr):
                    c = sig_color[s]
                    if c == 0 :
                        c = NO_GESTURE_POINT_COLOR
                    elif c == 1 :
                        c = GESTURE_POINT_COLOR
                    sig_pos = (i, ord_list[s]+self.sig_val[s, i])
                    pygame.draw.circle(self.monitor.surface, c, sig_pos, POINT_RADIUS, POINT_WIDTH)       
            
def m_map(x, current_min, current_max, target_min, target_max):
    return ((target_max-target_min)/(current_max-current_min))*x+((current_min*target_max-target_min*current_max)/(current_min-current_max))  
            
if __name__ == "__main__":
    
    monitor = Signal_Monitor(500, 200)
    queue = Queue()
    monitor.init_queue(queue)
    
    values = [0, 0, 0, 0]
    colors = [1, 0, 1, 0]
    
    queue.put((values, colors))   
    
    monitor.start()
    
    i = 0
    while True:
        values[0] = i%10
        values[1] = i%10  
        i +=1
        queue.put((values, colors))
       