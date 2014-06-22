# -*- encoding : utf-8 -*-

import numpy as np
import math as mth

# Distance Local Matrix
def local_dist(T, R, d_eval = lambda x,y : np.abs(x-y)):
    # T: Sequence Test; R: Sequence Reference
    n0,m0 = T.shape
    n1,m1 = R.shape
    d = np.zeros((n0,n1))    
    # Calcul matrice
    for i in range(n0):
        for j in range(n1):
            f_dist = np.sum(d_eval(T[i],R[j]))
            d[i,j] = f_dist#np.sqrt(f_dist)
            
    return d
        
# Global Distance Matrix
def global_dist(d, window_warping_adjustment, warp = lambda x,y,w,s : mth.fabs(x -(y/s))>w  ):
    # Initialisation
    r = window_warping_adjustment # Adjustement window size
    m,n = d.shape
    D = np.ones((m+1, n+1))
    D = np.Inf*D
    D[0][0] = d[0][0] # Initial Condition
    slp = n/float(m) # La pente de (0,0) a (m,n)
    steps = np.zeros((m,n)) # pas pour atteindre D(i,j)
    
    for i in range(m):
        for j in range(n):
            if (warp(i,j,r,slp)):
                continue
            # Calculate global distance
            t = [D[i+1,j] + d[i,j], D[i,j] + 2*d[i,j], D[i,j+1] + d[i,j]]
            # print t
            D[i+1,j+1] = np.min(t)
            steps[i,j] = np.argmin(t)
            
    # Time normalize global distance
    N = m + n
    D = D/N
    # Remove the 1st element
    D = np.delete(D,0,0)
    D = np.delete(D,0,1)
    return (D, steps)
    
# Recherche chemin optimal
def Traceback_path(steps):
    # Path matrix initialisation
    path = []
    i,j = steps.shape
    i = i-1
    j = j-1
    path.append([i,j])
    # Trace pathback from bottom rigth to top left
    while ((i>0) and (j>0)):
        if (steps[i][j]==0):
            # Antecedent D(i,j-1)
            j = j - 1
        elif (steps[i][j]==1):
            # Antecedent D(i-1,j-1)
            i = i - 1
            j = j - 1
        elif (steps[i][j]==2):
            # Antecedent D(i-1,j)
            i = i - 1
        else:
            print 'ERROR'
            
        path.append([i,j])
    path.append([0,0])
    return path[::-1]
    
# DTW
def DTW(T, R, window_warping_adjustement):
    d = local_dist(T,R)
    r = window_warping_adjustement
    D, steps = global_dist(d,r)
    path = Traceback_path(steps)
    min_D = D[-1][-1]
    return (min_D, path, D)                