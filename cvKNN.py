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
    return (Proto, Protoclass)

def Clustering(Centroid, Cluster, A, Proto, Protoclass):
    indx = MinInd(A,Centroid)
    T = np.nonzero(Cluster==indx)
    T = T[1]

    Prot = []
    Protclass = []    
    if len(T):
        for i in range(len(T)):
            d = T[i]
            Prot.append(Proto[d])
            Protclass.append(Protoclass[d])

    return (Prot, Protclass)

def MinInd(X,Centr):
    d_min = []
    h = len(Centr)
    m,n = np.shape(X)
    for i in range(h):
        m1,n1 = np.shape(Centr[i])
        r = np.fabs(np.fabs(m-m1) - min(m,m1))# this value Need to study for better results
        dm,pth,dis = cv.DTW(X, Centr[i], r)
        d_min.append(dm)
    ind = np.argmin(d_min)
    return ind

# K-NN ~1-KNN
def K_NN(X, Proto, Protoclass, K, Centroid=None, Cluster=None, debug = False):
    
    # Optimization option
    if Centroid != None and Cluster != None :
        Proto,Protoclass = Clustering(Centroid,Cluster,X,Proto,Protoclass)
    
    # Data loading
    labels = np.unique(Protoclass)
    d_min = []
    h = len(Proto)
    m,n = np.shape(X)
    mydict = []
    # Calcul, distances min
    for i in range(h):
        m1,n1 = np.shape(Proto[i])
        r = np.fabs(np.fabs(m-m1) - min(m,m1))# this value Need to study for better results
        dm,pth,dis = cv.DTW(X, Proto[i], r)
        mydict.append((Protoclass[i],dm))
        d_min.append(dm)
    # Classification
    if K==1:
        index = np.argmin(d_min)
        Xclass = Protoclass[index]
    else:
        # Classification
        S = sorted(mydict, key=lambda t:t[1])
        S = S[0:K]
        T = np.transpose(S)
        nClass = len(labels)
        classcount = []
        for i in range(nClass):
            x = list(map(lambda j: labels[i]==j, T[0]))
            classcount.append(np.sum(x))
        Xclass = np.argmax(classcount)
        Xclass = labels[Xclass]
    return Xclass         