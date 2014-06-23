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
    #h = len(Centr)
    m,n = np.shape(X)
    for i in Centr:
        m1,n1 = np.shape(i)
        r = np.fabs(np.fabs(m-m1) - min(m,m1))# this value Need to study for better results
        dm,pth,dis = cv.DTW(X, i, r)
        d_min.append(dm)
    ind = np.argmin(d_min)
    return ind

# K-NN ~1-KNN
def K_NN(X, Proto, Protoclass, K, Centroid=None, Cluster=None, debug = False):
    
    # Optimization option
    if Centroid is not None and Cluster is not None :
        Proto,Protoclass = Clustering(Centroid,Cluster,X,Proto,Protoclass)
    
    # Data laoding
    labels = np.unique(Protoclass)
    d_min = []
    h = len(Proto)
    m,n = np.shape(X)
    mydict = []
    # Calcul, distances min
    for i in xrange(h):
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
        #print T[0]
        nClass = len(labels)
        #print nClass
        classcount = []
        for i in xrange(nClass):
            x = map(lambda j: labels[i]==j, T[0])
            #print x
            classcount.append(np.sum(x))
        Xclass = np.argmax(classcount)
        Xclass = labels[Xclass]
    return Xclass         