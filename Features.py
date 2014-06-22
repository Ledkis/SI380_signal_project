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
    elif g < x < 2*g:
        x = 11 + np.fix(x/4)
    elif 0 < x < g:
        x = 1 + np.fix(x)
    elif x == 0:
        x = 0
    elif -g < x < 0:
        x = -1 + np.fix(x)
    elif -2*g < x < -g:
        x = -11 + np.fix(x/4)
    elif x < -2*g:
        x = -16
    return x

def quantvect(M):
    m,n = np.shape(M)
    for i in range(m):
        for j in range(n):
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
        for i in range(self.nrecs):
            M.append([np.mean(self.X[j:ws+j]),np.mean(self.Y[j:ws+j]),np.mean(self.Z[j:ws+j])])
            j = j + self.nadv
        M = np.array(M)
        M = quantvect(M)/(np.max(M) - np.min(M))
        return M
        
    def feat_Deviation(self):
        D = []
        X,Y,Z = self.X,self.Y,self.Z
        j = 0
        # Etape : Features Extraction
        # Deviation within a sliding window
        ws = self.wind
        for i in range(self.nrecs):
            D.append([np.var(X[j:ws+j]),np.var(Y[j:ws+j]),np.var(Z[j:ws+j])])
            j = j + self.nadv
        D = np.array(D)
        return D
    
    def feat_frequency(self):
        entropy = []
        E = []
        X,Y,Z = self.X,self.Y,self.Z
        # Entropy and power spectrum extraction
        j = 0
        ws = self.wind
        nfft = self.nfft
        nf = nfft/2
        for i in range(self.nrecs):
            xf = np.fft.fft(X[j:ws+j],nfft)/nfft
            yf = np.fft.fft(Y[j:ws+j],nfft)/nfft
            zf = np.fft.fft(Z[j:ws+j],nfft)/nfft
            a = np.abs(xf[0:nfft]-xf[0])**2
            b = np.abs(yf[0:nfft]-yf[0])**2
            c = np.abs(zf[0:nfft]-zf[0])**2
            E.append([np.sum(a[0:nf]),np.sum(b[0:nf]),np.sum(c[0:nf])])
            a = np.abs(a[0:nf])*2/nfft
            b = np.abs(b[0:nf])*2/nfft
            c = np.abs(c[0:nf])*2/nfft
            dx = a/np.sum(a + 1e-12)
            logdx = np.log2(dx + 1e-12)
            dy = b/np.sum(b + 1e-12)
            logdy = np.log2(dy + 1e-12)
            dz = c/np.sum(c + 1e-12)
            logdz = np.log2(dz + 1e-12)
            entropy.append([-np.sum(dx*logdx)/np.log2(nf),-np.sum(dy*logdy)/np.log2(nf),
                    -np.sum(dz*logdz)/np.log2(nf)])
            j = j + self.nadv
            
        E = np.array(E)
        entropy = np.array(entropy)
        return E,entropy
    
    def features_extract(self):
        self.Mean = self.feat_Mean()
        self.Dev = self.feat_Deviation()
        self.E,self.Entropy = self.feat_frequency()