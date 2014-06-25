# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 16:30:29 2014

@author: many
"""

import cvDTW
import numpy as np

def isRand(Proto,Protoclass,k):
    # To be sure of the initialization we can select data that we will introduce
    # as centroid in each class
    Protoclass = np.array(Protoclass)
    label = list(set(Protoclass))
    V = (np.nonzero(Protoclass==i)[0] for i in label)
    D = (j[0] for j in V)
    C = [Proto[i] for i in D]
    C = np.array(C)
    return C   

def DistMat(A,B):
    # B centroid and A vector
    c = len(B)
    h = len(A)
    D = np.zeros((h,c))
    C = B
    for j in xrange(h):
        Dc = []
        P = []
        for i in xrange(c):
            d_min,p,d = cvDTW.DTW(A[j],B[i])
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
    for i in xrange(m):
        nC[path[i][1]] = (nC[path[i][1]] + B[path[i][0]])/2
    return nC
            
def kmeans(dataset,labels, k):
    # centroid initialization
    C = isRand(dataset,labels,k)
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