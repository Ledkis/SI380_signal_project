# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 16:30:29 2014

@author: many
"""

import cvDTW
import numpy as np

import sys
if sys.version_info < (3,):
    range = xrange

def isRand(Proto,k):
    # h = len(Proto)
    #d = np.random.permutation(h)
    # To be sure of the initialization we can select data that we will introduce
    # as centroid in each class
    a = 0 
    d = [a+1, a+4, a+8, a+12]
    D = d[:k]
    C = []
    for i in D:
       C.append(Proto[i]) 
    C = np.array(C)
    return C   

def DistMat(A,B):
    # B centroid and A vector
    c = len(B)
    h = len(A)
    D = np.zeros((h,c))
    C = B
    for j in range(h):
        m1,n1 = np.shape(A[j])
        Dc = []
        P = []
        for i in range(c):
            m,n = np.shape(B[i])
            r = np.fabs(np.fabs(n-n1) - min(n,n1))
            d_min,p,d = cvDTW.DTW(A[j],B[i],r)
            Dc.append(d_min)
            P.append(p)
            D[j][i]=d_min 
        ind = np.argmin(Dc)
        path = P[ind]
        nC = Centroid(B[ind],A[j],path)
        C[ind] = nC
    return D,C

def Centroid(C,B,path):
    # C centroid and B vector to cluster
    path = np.array(path)
    m = len(path)
    nC = C
    for i in range(m):
        nC[path[i][1]] = (nC[path[i][1]] + B[path[i][0]])/2
    return nC
            
def kmeans(dataset, k):
    # centroid initialization
    C = isRand(dataset,k)
    # Main loop
    me = 1
    h = len(dataset)
    # initialization of vetor zero
    temp = np.zeros((1,h))
    
    while me:
        # Expectation step
        D,nC = DistMat(dataset,C)
        g = np.argmin(D,axis=1)
        g = np.tile(g,(1,1))
        if np.all(g==temp):
            me=0
        else:
           temp = g
           C = nC
    
    return C,g