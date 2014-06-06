# -*- coding: utf-8 -*-
"""
K NN Classifier
"""
import m_log as log
import numpy as np
import cvDTW as cv

# Data design
def Data_design(A,debug=False):
    labels = A.keys()
    
    if len(labels) == 0:
        log.d("[Data_design]", 'There is no reference Classes', debug)
        return None
    Proto = []
    Protoclass = []    
    if len(labels):
        for i in range(len(labels)):
            R = A[labels[i]]
            if len(R):
                for j in range(len(R)):
                    Proto.append(R[j])
                    Protoclass.append(labels[i])
            if len(R) == 0:
                log.d("[Data_design]", 'Error empty Class', debug)
                return None
    return (labels, Proto, Protoclass)

# K-NN ~1-KNN
def K_NN(X, A, K = 1, debug = False):    
    # Data laoding
    labels, Proto, Protoclass = Data_design(A,True)
     
    d_min = []
    h = len(Proto)
    m,n = np.shape(X)
    
    # Calcul, distances min
    for i in range(h):
        m1,n1 = np.shape(Proto[i])
        r = np.fabs(np.fabs(n-n1) - min(n,n1))# this value Need to study for better results
        dm,pth,dis = cv.DTW(X, Proto[i], r)
        d_min.append(dm)
    # Classification
    if K==1:
        index = np.argmin(d_min)
        Xclass = Protoclass[index]
    else:
        mydict = {key:value for key,value in zip(Protoclass,d_min)}
        # Classification
        S = sorted(mydict.items(), key=lambda t:t[1])
        S = S[0:K]
        nClass = len(labels)
        classcount = []
        for i in range(nClass):
            x = map(lambda j: labels[i]==j, S.keys())
            classcount.append(np.sum(x))
        Xclass = np.argmax(classcount)
    return Xclass         