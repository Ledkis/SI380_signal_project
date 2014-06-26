# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 07:58:14 2014

@author: many
"""
import numpy as np
import PreProcess as PreP

def nextpow2(n):
    i = 1
    while i < n: i *= 2
    return i

def quantif(x):
    g = 9.81
    if x > 2*g:
        x = 16
    if g < x < 2*g:
        x = 11 + np.fix(x/4)
    if 0 < x < g:
        x = 1 + np.fix(x)
    if x == 0:
        x = 0
    if -g < x < 0:
        x = -1 + np.fix(x)
    if -2*g < x < -g:
        x = -11 + np.fix(x/4)
    if x < -2*g:
        x = -16
    return x

def quantvect(M):
    m,n = np.shape(M)
    for i in xrange(m):
        for j in xrange(n):
            M[i][j] = quantif(M[i][j])
    return M
            
class features():
    def __init__(self, x, wind = 20, over = 50):
        self.vect = x
        self.wind = wind
        self.over = over
        self.nover = np.fix(self.wind*self.over/100)
        self.nadv = self.wind - self.nover
        self.nrecs = np.fix((len(x) - self.nover)/self.nadv)       
        self.nfft = nextpow2(self.wind)
        self.X,self.Y,self.Z = PreP.FIR2(self.vect)
    
    def feat_Mean(self):
        M = []
        j = 0
        # Etape : Features Extraction
        # Mean within a sliding window
        ws = self.wind
        
        for i in xrange(self.nrecs):
            M.append([np.mean(self.X[j:ws+j]),np.mean(self.Y[j:ws+j]),np.mean(self.Z[j:ws+j])])
            j = j + self.nadv
        #M = quantvect(np.array(M))
        M = np.array(M)
        #M = quantvect(M)/(np.max(M) - np.min(M))
        M = M/(np.max(M) - np.min(M))
        return M
        
    def feat_Deviation(self):
        D = []
        X,Y,Z = self.X,self.Y,self.Z
        R = []
        for i in xrange(len(X)):
            R.append([X[i],Y[i],Z[i]])

        R = quantvect(R)
        R1 = np.transpose(R)
        for i in xrange(3):
            R1[i] = R1[i]/(np.max(R1[i]) - np.min(R1[i]))
        R = np.transpose(R1)

        X = np.array([row[0] for row in R])
        Y = np.array([row[1] for row in R])
        Z = np.array([row[2] for row in R])
        
        j = 0
        # Etape : Features Extraction
        # Deviation within a sliding window
        ws = self.wind
        for i in xrange(self.nrecs):
            D.append([np.var(X[j:ws+j]),np.var(Y[j:ws+j]),np.var(Z[j:ws+j])])
            j = j + self.nadv
        D = np.array(D)
        return D
    
    def feat_frequency(self):
        E = []
        X,Y,Z = self.X,self.Y,self.Z
        # Entropy and power spectrum extraction
        j = 0
        ws = self.wind
        nfft = self.nfft
        nf = nfft/2
        for i in xrange(self.nrecs):
            xf = np.fft.fft(X[j:ws+j],nfft)/nfft
            yf = np.fft.fft(Y[j:ws+j],nfft)/nfft
            zf = np.fft.fft(Z[j:ws+j],nfft)/nfft
            a = np.abs(xf[0:nfft]-xf[0])**2
            b = np.abs(yf[0:nfft]-yf[0])**2
            c = np.abs(zf[0:nfft]-zf[0])**2
            E.append([np.sum(a[0:nf]),np.sum(b[0:nf]),np.sum(c[0:nf])])
            
            j = j + self.nadv
            
        E = np.array(E)
        E = E/(np.max(E) - np.min(E))
        return E
        
    def mean_nrj(self):
        m = self.feat_Mean()
        nrj = self.feat_frequency()
        n = len(m)
        data = np.array([[m[i][0],m[i][1],m[i][2],nrj[i][0],nrj[i][1],
                         nrj[i][2]] for i in xrange(n)])
        return data
        
    def features_extract(self):
        self.Mean = self.feat_Mean()       
        #self.Dev = self.feat_Deviation()
        #self.E = self.feat_frequency()
        #self.param = self.mean_nrj()