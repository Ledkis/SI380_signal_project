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
    
class features():
    def __init__(self, x, wind = 20, over = 50):
        self.vect = x
        self.wind = wind
        self.over = over
        self.nover = np.fix(self.wind*self.over/100)
        self.nadv = self.wind - self.nover
        self.nrecs = np.fix((len(x) - self.nover)/self.nadv)       
        self.nfft = nextpow2(self.wind)
        self.X,self.Y,self.Z = PreP.FIR2(self.x)
    
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
        nf1 = nf - 1
        for i in range(self.nrecs):
            xf = np.fft.fft(X[j:ws+j],nfft)/nfft
            yf = np.fft.fft(Y[j:ws+j],nfft)/nfft
            zf = np.fft.fft(Z[j:ws+j],nfft)/nfft
            a = np.abs(xf[1:nf])**2/nf1
            b = np.abs(yf[1:nf])**2/nf1
            c = np.abs(zf[1:nf])**2/nf1
            E.append([np.sum(a),np.sum(b),np.sum(c)])
            dx = a/np.sum(a + 1e-12)
            logdx = np.log2(dx + 1e-12)
            dy = b/np.sum(b + 1e-12)
            logdy = np.log2(dy + 1e-12)
            dz = c/np.sum(c + 1e-12)
            logdz = np.log2(dz + 1e-12)
            entropy.append([-np.sum(dx*logdx)/np.log2(nf1),-np.sum(dy*logdy)/np.log2(nf1),
                    -np.sum(dz*logdz)/np.log2(nf1)])
            j = j + self.nadv
            
        E = np.array(E)
        entropy = np.array(entropy)
        return E,entropy
    
    def features_extract(self):
        self.Mean = self.feat_Mean(self)
        self.Dev = self.feat_Deviation(self)
        self.E,self.Entropy = self.feat_frequency(self)