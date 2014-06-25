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
        for i in labels:
            R = A[i]
            if len(R):
                for j in R:
                    Proto.append(j)
                    Protoclass.append(i)
            if len(R) == 0:
                log.d("[Data_design]", 'Error empty Class', debug)
                return None
    return (Proto, Protoclass)
    
def Clustering(Centroid, Cluster, A, Proto, Protoclass):
    indx = MinInd(A,Centroid)
    T = np.nonzero(Cluster==indx)
    T = T[1]
    
    if len(T):
        Prot= [Proto[i]for i in T]
        Protclass = [Protoclass[i] for i in T]

    return (Prot, Protclass)

def MinInd(X,Centr):
    d_min = []

    for i in Centr:
        dm = cv.DTW1(X, i)
        d_min.append(dm)
    ind = np.argmin(d_min)
    return ind

# K-NN ~1-KNN
def K_NN(X, Proto, Protoclass, K, Centroid=None, Cluster=None):
    
    # Optimization option
    if Centroid is not None and Cluster is not None :
        Proto,Protoclass = Clustering(Centroid,Cluster,X,Proto,Protoclass)
    
    # Data laoding
    labels = np.unique(Protoclass)
    d_min = []
    h = len(Proto)
    mydict = []
    # Calcul, distances min
    for i in xrange(h):      
        d_min.append(cv.DTW1(X, Proto[i]))
        mydict.append((Protoclass[i],d_min[i]))

    # Classification
    if K==1:
        index = np.argmin(d_min)
        return Protoclass[index]
    else:
        # Classification
        S = sorted(mydict, key=lambda t:t[1])
        S = S[0:K]
        T = np.transpose(S)
        V = (np.nonzero(T[0]==i)[0] for i in labels)
        D = np.argmax((len(j) for j in V))
        return labels[D]         