# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 07:37:15 2014

@author: many
"""

import numpy as np

def gaussian_kernel(size,sigma):
    size = int(size)
    if not sigma:
        sigma = 1.0
    else:
        sigma = float(sigma)
    x = np.linspace(-size/2, size/2, size)
    g = np.exp(-(x**2) / (2*(sigma**2)))/(np.sqrt(2*np.pi)*sigma)
    g = np.array(g)
    return g/np.sum(g)     

def FIR1(x):
    # Etape : High pass filter for gravity noise reduction
    factor = 0.7
    X = np.array([row[0] for row in x])
    Y = np.array([row[1] for row in x])
    Z = np.array([row[2] for row in x])
    
    m,n = np.shape(x) 
    
    X = np.array(X) - np.mean(X)
    Y = np.array(Y) - np.mean(Y)
    Z = np.array(Z) - np.mean(Z)
    X1,Y1,Z1 = X,Y,Z
    
    # high pass filter
    for i in range(m-1):
        X1[i+1] = factor*(X[i+1] - X[i]) + factor*X1[i]
        Y1[i+1] = factor*(Y[i+1] - Y[i]) + factor*Y1[i]
        Z1[i+1] = factor*(Z[i+1] - Z[i]) + factor*Z1[i]
    
    return X1,Y1,Z1
    
def FIR2(x):
    X1,Y1,Z1 = FIR1(x)
    
    # gaussian filter
    q=10
    std = 1
    g = gaussian_kernel(q,std)
    X2 = np.convolve(g,X1,'same')
    Y2 = np.convolve(g,Y1,'same')
    Z2 = np.convolve(g,Z1,'same')
    
    return X2,Y2,Z2   