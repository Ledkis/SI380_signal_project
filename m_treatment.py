# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 14:21:15 2014

@author: Utilisateur
"""

from m_buffer import Buff, dim_mean, dim_sum
import m_log as Log

import numpy as np
import datetime

BUFF_LEN = 15
G_CONST = 9.81

MAX_GESTURE_LENGTH = 150

FREQ_LEN_DATA = 100

SAVED_ACC = 50

EPS = 0.00001

TAG = "Data_Treatment"

parms = {"m_acc_l" : 10,
         "m_teta_l" : 15, 
         "cuted_val_nbr" : 5,
         "m_g_proj_l" : 15, 
         "m_n_norm_l" : 30}

class Data_Treatment():
    def __init__(self):
        self.debug = True
        self.c_debug = True
        self.queue = None
        
        self.kill_gravity = True
        self.kill_rot = True
        self.kill_low_gesture = True
        self.decc_detection = False
        
        self.n_norm = 0
        self.n_norm_buff = Buff(1, parms["m_n_norm_l"])        
        self.m_n_norm = 0
        self.m_n_norm_buff = Buff(1, 5)
        self.m2_n_norm = 0
        self.m2_n_norm_buff = Buff(1, 3)
        self.last_m2_n_norm = 0
        
        self.g_proj =  np.array([0, 0, 0])
        self.g_proj_buff = Buff(3, parms["m_g_proj_l"])
        self.m_g_proj =  np.array([0, 0, 0])
        self.ge_m_g_proj =  np.array([0, 0, 0])
        
        self.teta = 0
        self.teta_buff = Buff(1, parms["m_teta_l"])
        self.m_teta = 0
        self.ge_m_teta = 0
        self.rot_mat = np.eye(3)
        self.ge_rot_mat = np.eye(3)
        
        self.incr_flag = False
        self.decr_flag = False
        self.last_max_pic = 0
        self.last_min_pic = 0
        
        self.pic_p = np.array([0, 0]) #Val, color
        
        self.energy_seuil = 2
        self.ge_seuil = 20
        self.tail = 10
        self.no_ge_seuil = 5
        self.decc_seuil = 2
        
        self.cuted_val_nbr = parms["cuted_val_nbr"]
        self.gesture_state = 0
        self.gesture_state_buff = Buff(1, self.ge_seuil)
        
        self.delayed_m2_n_norm_buf = Buff(2, MAX_GESTURE_LENGTH)
        
        self.acc = np.array([0, 0, 0])
        self.acc_buff = Buff(3, parms["m_acc_l"])
        self.m_acc = np.array([0, 0, 0])
        self.m_acc_buff = Buff(3, SAVED_ACC)
        self.n_a = np.array([0, 0, 0])
        self.ge_n_a = np.array([0, 0, 0])
        self.ge_n_a_buff = Buff(3, self.ge_seuil)
        
        self.gesture = []
        self.gesture_len = 0
        self.c_gesture = None
        
        
        self.freq_buff = Buff(1, FREQ_LEN_DATA)
        self.start_t = 0
        self.time_l = 0
        self.m_freq = 0
        
        self.monitored_attr_names = ["m_n_norm"]
        
        self.sig_color = [0]
        
    def _monitor(self, sig_val, sig_color):
        if self.queue is not None:
            self.queue.put((sig_val, sig_color))
            
    def _plot_data(self, queue):
        if not (self.queue is not None):
            self.queue = queue
          
        delayed_norm_val, delayed_norm_color = self.delayed_m2_n_norm_buf.data[:, 0]
        
        sig_val = []
        for attr_name in self.monitored_attr_names:
            attr_info = attr_name.split("-")
            attr_name = attr_info[0]
            i = None
            if len(attr_info) > 1:
                i = int(attr_info[1])
                
            attr = getattr(self, attr_name)
            if type(attr) == np.ndarray:
                if i is None:
                    sig_val += list(attr)
                else:
                    sig_val += [attr[i]]
            else:
                sig_val += [attr]
        
        l= len(sig_val)
        if l !=0:
            self._monitor(sig_val, self.sig_color*l)
        self.pic_p = np.array([0, 0])
        
    def set_monitored_attr(self, *args):
        self.monitored_attr_names = []
        for attr_info in args:
            attr_name = attr_info.split("-")[0]
            try:
                getattr(self, attr_name)
                self.monitored_attr_names += [attr_info]
            except AttributeError:
                Log.d(TAG, "The attribute %s doesn't exist"%(attr_name), self.debug)
                

    def perform(self, acc_values, continuous, queue = None):
        self.start_t = datetime.datetime.now()
        
        self.acc = np.array(acc_values)
        self.acc_buff.update(self.acc)
        self.m_acc = dim_mean(self.acc_buff)
        self.m_acc_buff.update(self.m_acc)
        
        self._eval_gesture_state()
        self._eval_gesture_normalized_acc()        
        

        self._plot_data(queue)
        
        self._eval_freq()
        if continuous:
            return self.c_gesture
        else:
            return None
            
        
    def _eval_gesture_state(self):
        
        if self.c_gesture is not None:
            self.c_gesture = None
        
        self._eval_g_proj()
        self._eval_rot()
        self._set_n_acc()
        self._eval_energy()
        self._tcheck_gesture_state()
        
    def _eval_freq(self):
        self.time_l = (datetime.datetime.now()-self.start_t).total_seconds()
        freq = 1/self.time_l
        self.freq_buff.update(freq)
        self.m_freq = np.mean(self.freq_buff.data)
        
    def _eval_gesture_normalized_acc(self):
                    
        self.ge_n_a = self._renorm(self.m_acc, self.ge_rot_mat, self.ge_m_g_proj)
        Log.d(TAG, "ge_n_a = %s"%(self.ge_n_a), True)
        
        self.ge_n_a_buff.update(self.ge_n_a)
        
        if self.gesture_state:
            self._update_gesture(self.ge_n_a)
        
    def _eval_g_proj(self):
        self.g_proj = np.copy(self.m_acc)
        self.g_proj_buff.update(self.g_proj)
        self.m_g_proj = dim_mean(self.g_proj_buff, k = self.cuted_val_nbr)
        
    def _eval_rot(self):
        a_x, a_y, a_z = self.m_acc
        self.teta = np.arctan(-a_x/a_z)
        
        if a_x > 0 and a_z < 0:
            self.teta = -np.pi + self.teta
        if a_x < 0 and a_z < 0:
            self.teta = np.pi + self.teta
            
        self.teta_buff.update(self.teta)
        self.m_teta, = dim_mean(self.teta_buff,  k = self.cuted_val_nbr )
        
        self.rot_mat = np.array([[np.cos(self.m_teta), 0, np.sin(self.m_teta)],
                            [0, 1, 0],
                            [-np.sin(self.m_teta), 0, np.cos(self.m_teta)]])
                            
    def _set_n_acc(self):
        self.n_a = self._renorm(self.m_acc, self.rot_mat, self.m_g_proj)
                            
    def _eval_energy(self):
        self.n_norm = np.sqrt(self.n_a[0]**2 + self.n_a[1]**2 + self.n_a[2]**2)
        self.n_norm_buff.update(self.n_norm)
        
        self.m_n_norm = np.mean(self.n_norm_buff.data)/self.energy_seuil 
        
#        self.m_n_norm_buff.update(self.m_n_norm)
#        self.last_m2_n_norm = self.m2_n_norm
#        self.m2_n_norm = np.mean(self.m_n_norm_buff.data)/self.energy_seuil 
        
        self.delayed_m2_n_norm_buf.update(np.array([self.m2_n_norm,0]))
        
    def _tcheck_gesture_state(self):
        
        if self.kill_low_gesture:
            state = -1
            if self.m_n_norm > self.energy_seuil:
                # A mouvment is detected
                #Log.d(TAG, "A mouvment is detected", True)
                state = 1
                if self._tcheck_decc():
                    return
                
            self.gesture_state_buff.update(state)
            self._tcheck_energy()
        else:
            if self.m_n_norm > self.energy_seuil:
                self._set_gesture_state(True)
                self._tcheck_decc()
            else:
                self._set_gesture_state(False)

    def _tcheck_decc(self):
        
        decc_detected = False
        
        if self.decc_detection:
        
            if self.incr_flag and (self.m2_n_norm < self.last_m2_n_norm):
                self.last_max_pic = self.last_m2_n_norm
                self.pic_p = np.array([self.last_max_pic, 1])
                
            if self.decr_flag and (self.m2_n_norm > self.last_m2_n_norm):
                self.last_min_pic = self.last_m2_n_norm
                self.pic_p = np.array([self.last_min_pic, 2])
                
                if (self.last_min_pic > self.energy_seuil) and \
                    self.last_max_pic - self.last_min_pic > self.decc_seuil:
                        
                    Log.d(TAG, "Decc detected !", self.debug)
                    self._set_gesture_state(False)
                    decc_detected = True
            
            if (self.m2_n_norm > self.last_m2_n_norm):
                self.incr_flag, self.decr_flag = True, False
            else :
                self.incr_flag, self.decr_flag = False, True
            
        return decc_detected
        
    def _tcheck_energy(self):
        if self.gesture_state:
            no_move_length, = dim_sum(self.gesture_state_buff, e_off = self.no_ge_seuil)
            no_gesture_cond = (no_move_length == -self.no_ge_seuil)
            
            i_e = self.delayed_m2_n_norm_buf.buff_len
            self.delayed_m2_n_norm_buf.change_dim_data(1, i_e-1, i_e, [1])
            
            if no_gesture_cond:
                self._set_gesture_state(False)
                        
        else:
            move_length, = dim_sum(self.gesture_state_buff, e_off = self.ge_seuil)
            gesture_cond = (move_length == self.ge_seuil)
            
            i_e = self.delayed_m2_n_norm_buf.buff_len
            self.delayed_m2_n_norm_buf.change_dim_data(1, i_e-1, i_e, [0])
            
            if gesture_cond:
                self._set_gesture_state(True)
                
                # We add the acceleration values used to switch in gesture mode
                i_s = self.delayed_m2_n_norm_buf.buff_len-self.ge_seuil
                i_e = self.delayed_m2_n_norm_buf.buff_len
                
                for tail_acc in self.m_acc_buff.data[:, SAVED_ACC-self.ge_seuil+self.tail:].T:
                    g_acc = self._renorm(tail_acc, self.ge_rot_mat, self.ge_m_g_proj)
                    self._update_gesture(g_acc)
                    
                self.delayed_m2_n_norm_buf.change_dim_data(1, i_s, i_e, [1]*self.ge_seuil)
                
                self.gesture_len = self.ge_seuil
                
            
    def _set_gesture_state(self, gesture_state):
        gesture_state = int(bool(gesture_state))
        if not self.gesture_state == gesture_state:
            self.gesture_state = gesture_state
            if self.gesture_state:
                self.ge_m_teta = self.m_teta
                self.ge_rot_mat = np.copy(self.rot_mat)
                self.ge_m_g_proj = np.copy(self.m_g_proj)
                self.sig_color = [1]
                Log.d(TAG, "Gesture Detected", self.debug)
                
                #TODO : Moche
                if not self.kill_low_gesture:
                    for tail_acc in self.m_acc_buff.data[:, SAVED_ACC-self.ge_seuil+self.tail:].T:
                        g_acc = self._renorm(tail_acc, self.ge_rot_mat, self.ge_m_g_proj)
                        self._update_gesture(g_acc)
            else:
                self.c_gesture = self.gesture[:]
                self.gesture = []
                self.sig_color = [0]
                Log.d(TAG, "End Gesture", self.debug)
                
    def _update_gesture(self, g_acc):
        if len(self.gesture) == 0:
            Log.d(TAG, "Add gesture meta data", self.debug)
            meta_data = (self.ge_m_teta, self.ge_m_g_proj)
            self.gesture.append(meta_data)
        self.gesture.append(g_acc)
                
    def _renorm(self, acc, rot_mat, g_proj):
        n_a = acc
        if self.kill_gravity:
            n_a = n_a - g_proj
        if self.kill_rot:
            n_a = rot_mat.dot(n_a)
        return n_a