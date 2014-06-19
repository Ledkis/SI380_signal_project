# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 19:25:16 2014

@author: Utilisateur
"""

import numpy as np

class Buff():
    def __init__(self, buff_dim, buff_len):
        self.buff_dim = buff_dim
        self.buff_len = buff_len
        self.data = np.zeros((self.buff_dim, self.buff_len))
        
    
    def update(self, val):
        for i in range(1, self.buff_len):
            self.data[:, i-1] = self.data[:, i]
            
        self.data[:, -1] = val
        
    def set_len(self, new_len):
        old_len = self.buff_len
        old_data = np.copy(self.data)
        if old_len > new_len:
            old_data = old_data[:, -new_len:]
            l = new_len
        else :
            l = old_len
            
        self.buff_len = new_len
        self.data = np.zeros((self.buff_dim, self.buff_len))
        self.data[:, -l:] = old_data
        
    def change_dim_data(self, dim, i_s, i_e, vals):
        self.data[dim, i_s:i_e] = vals
        
    def change_data(self, i_s, i_e, vals):
        self.data[:, i_s:i_e] = vals
        
        
def m_energy(buff):
    return tuple(np.sqrt(np.sum(np.array([j**2 
            for j in dim])))/buff.buff_len for dim in buff.data)
                
def m_norm(buff):
    return tuple(np.sqrt(np.sum(dim**2)) for dim in buff.data)
    
def dim_mean(buff, k = 0):
    return np.array([np.mean(dim) for dim in buff.data[:, :buff.buff_len-k]])
    
def dim_sum(buff, e_off = 0):
    return tuple(np.sum(dim) for dim in buff.data[:, buff.buff_len-e_off:])
    
if __name__ == "__main__":
    a = Buff(2, 5)
    
    a.update([1, 2])
    a.update([3, 4])
    a.update([5, 6])
    a.update([7, 8])
    a.update([9, 0])
