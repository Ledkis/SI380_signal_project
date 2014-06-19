# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 21:50:40 2014

@author: Utilisateur
"""

# TODO : to optimize with numpy

import m_log as Log
from m_buffer import Buff

import time

import traceback
from multiprocessing import Process, Queue, TimeoutError
import numpy as np
import pygame
import pygame.locals

MAX_SIG = 10

BACKGROUND_COLOR = (255, 255, 255)

DEFAULT_POINT_COLOR = (0, 255, 0)
GESTURE_POINT_COLOR = (255, 0, 0)
NO_GESTURE_POINT_COLOR = (0, 0, 255)
AXIS_COLOR = (0, 0, 0)
Z_POINT_COLOR = (0, 0, 0)

MIN_VAL = 10
MAX_VAL = -10

X_AXIS_SPACE = 1
Y_AXIS_SPACE = 100
Y_AXIS_NARROW_SPACE = 10

POINT_RADIUS = 1
POINT_WIDTH = 0

FRAMERATE = 100

class Signal_Monitor(Process):
    def __init__(self, queue, width_px, height_px, title = "Signal_Monitor", debug = True):
        super(Signal_Monitor, self).__init__()
        self.queue = queue
        self.title = title
        self.width_px, self.height_px = width_px, height_px
        
        self.debug = debug
        self.TAG = "Signal_Monitor"
        Log.d(self.TAG, "Initialized", self.debug)
        
    def run(self):
        
        pygame.init()
        
        self.surface = pygame.display.set_mode((self.width_px, self.height_px), pygame.locals.RESIZABLE)
        pygame.display.set_caption(self.title)
        self.surface.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        
        Log.d(self.TAG, "Window ready loop", self.debug)
        
        self.clock = pygame.time.Clock()
        self.done = False
        
        self.monitor = Signal_Display(self)
        
        Log.d(self.TAG, "Start loop", self.debug)
    
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
                #Log.d(self.TAG, "queue length : %s"%(self.queue.qsize()), self.debug)
                self.surface.fill(BACKGROUND_COLOR)
                
                try:
                    self.monitor.draw(sig_val, sig_color)
                except:
                    traceback.print_exc()
                
                pygame.display.flip()
                
                del sig_val
                del sig_color
                
            except TimeoutError:
                pass
            
        pygame.quit()
        
class Signal_Display():
    def __init__(self, monitor, debug = True):
        self.monitor = monitor
        
        self.sig_points_buff = [Buff(2, self.monitor.width_px) for i in range(MAX_SIG)]
        self.draw_nbr = 0
        
        self.debug = debug
        self.TAG = "Signal_Display"
        Log.d(self.TAG, "Initialized", self.debug)
        
        
    def update_data(self, sig_val, sig_color):
        sig_size = len(sig_val)
        for i in range(sig_size):
            self.sig_points_buff[i].update([sig_val[i], sig_color[i]])
        
    def remap_y_pos(self, y_pos):
        return int(m_map(y_pos, MIN_VAL, MAX_VAL, -self.max_height, self.max_height))
          
    def eval_sig_ord(self, sig_nbr):
        self.max_height = self.monitor.height_px/(2*sig_nbr)
        return tuple([int((2*i+1)*self.max_height) for i in range(sig_nbr)])
        
    def draw(self, sig_val, sig_color):
        sig_nbr = len(sig_val)
        
        if sig_nbr == 0:
            Log.d(self.TAG, "No signal to display", self.debug)
            return
        
        ord_list = self.eval_sig_ord(sig_nbr)
        
        if not self.monitor.done:
            self.draw_vert_axes(ord_list, sig_nbr)
            self.draw_horz_axis()
            
            self.update_data(sig_val, sig_color)
            
            for i in range(self.monitor.width_px):
                for s in range(sig_nbr):
                    
                    c = self.sig_points_buff[s].data[1, i]
                    if c == 0 :
                        c = NO_GESTURE_POINT_COLOR
                    elif c == 1 :
                        c = GESTURE_POINT_COLOR
                    elif c == 2 :
                        c = DEFAULT_POINT_COLOR
                        
                    ord_p = ord_list[s]
                    sig_y_pos = self.remap_y_pos(self.sig_points_buff[s].data[0, i])+ord_p
                    sig_pos = (i, sig_y_pos)
                    
                    pygame.draw.circle(self.monitor.surface, c, sig_pos, POINT_RADIUS, POINT_WIDTH)
        self.draw_nbr += 1
            

    def draw_vert_axes(self, ord_list, sig_nbr):
        for s in range(sig_nbr):
            mi = -abs(MIN_VAL)+1
            mx = abs(MAX_VAL)
            for i in range(mi, mx, X_AXIS_SPACE):
                ord_p = ord_list[s]
                #0 x axis
                y_p = ord_p+self.remap_y_pos(i)
                s_p, e_p = (0, y_p), (self.monitor.width_px, y_p)
                width = 1
                if i == mi or i == mx-1 or i == 0:
                    width = 2
                pygame.draw.line(self.monitor.surface, AXIS_COLOR, s_p, e_p, width)
    
    def draw_horz_axis(self):
        for i in range(0, self.monitor.width_px, Y_AXIS_SPACE):
            s_p, e_p = (i, 0), (i, self.monitor.height_px)
            pygame.draw.line(self.monitor.surface, AXIS_COLOR, s_p, e_p, 1)
        for i in range(0, Y_AXIS_SPACE, Y_AXIS_NARROW_SPACE):
            s_p, e_p = (i, 0), (i, self.monitor.height_px)
            pygame.draw.line(self.monitor.surface, AXIS_COLOR, s_p, e_p, 1)
        
def m_map(x, current_min, current_max, target_min, target_max):
    return ((target_max-target_min)/(current_max-current_min))*x+((current_min*target_max-target_min*current_max)/(current_min-current_max))  
            
if __name__ == "__main__":
    
    import threading
    
    queue = Queue()
    
    class Pyg(threading.Thread): 
        def __init__(self, queue, name = 'bla'): 
            threading.Thread.__init__(self)
            self.name = name
            self.queue = queue

        def run(self): 
            monitor = Signal_Monitor(self.queue, 500, 1000)
            monitor.start()
    
    def launch_pyg(): 
        monitor = Signal_Monitor(queue, 500, 1000)
        monitor.init_queue(queue)
        monitor.start()
  
    values = [0, 0, 0, 0]
    colors = [1, 0, 1, 0]
    
    queue.put((values, colors))  
    
    #threading.Thread(None, launch_pyg, None).start()
    
    pyg = Pyg(queue, "hi")
    pyg.start()
    
    
    i = 0
    while True:
        time.sleep(1/FRAMERATE)
        values[0] = i%10
        values[1] = i%10  
        i +=1
        queue.put((values, colors))
       