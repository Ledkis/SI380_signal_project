# -*- encoding : utf-8 -*-

import numpy as np


def eucl_dist(x, y):
    """Compute the euclidian distance between vector x and y.
    """
    return np.sqrt(np.sum((x-y)**2))
    


def eval_distance_matrix(s1, s2,  d_eval = lambda x,y : (x - y)**2):
    """Evaluate the distance matrix between the time series s1 and s2 using
    the distance d_eval.
    
    Parameter
    s1 -- time serie n°1    
    s2 -- time serie n°2
    d_val -- distance between s1(i) and s2(j)
            By default : d_val(i,j) = (s1(i)-s2(j))**2
    
    """
    
    nn = s1.size
    mm = s2.size
    
    #Initialisation of the distance matrix
    D = np.zeros((nn, mm));
    
    for i in range(nn):
        for j in range(mm):
            D[i, j] = d_eval(s1[i], s2[j])
            
    return D
    
def eval_cummuled_distance_matrix(D, r = None, warping_window = lambda i,j,r : i-r<=j<=i+r):
    """Evaluate the cummuled distance matrix W from a distance matrix D
    
    Parameter
    D -- distance matrix
    r -- wraping windows
    """
    
    #Use warping or not
    warp = False
    if r is not None:
        warp = True
    
    nn, mm = np.shape(D)
    W = np.zeros((nn, mm))
    
    #REM : We will use there a Symetric DTW wit warping windows and no slope constraint
    
    for i in range(nn):
        for j in range(mm):
            #Initialisation
            if i == j == 0:
                W[i, j] = D[0, 0]
            else:
                if not (warp and warping_window(i, j, r)):
                    continue;
                d = []
                if i > 0:
                    d.append(W[i-1, j] + D[i, j])
                if i > 0 and j > 0:
                    d.append(W[i-1, j-1] + 2*D[i, j])
                if j > 0:
                    d.append(W[i, j-1] + D[i,j])
                W[i,j] = min(d)
    return W
    
	
def display_row_inverted_matrix(D):
    """Display the distance matrix with the origin in the bottom left corner.
	"""
    D = np.flipud(D)
    print(D)

    
    
	
if __name__ == "__main__":
    
    s1 = np.array([1, 2, 2, 4, 6])
    s2 = np.array([2, 3, 4, 5, 6, 7])
    s3 = np.array([1, 2, 4, 4, 6, 6])
    
    D1 = eval_distance_matrix(s2, s1)
    D2= eval_distance_matrix(s3, s1)
    
    
    display_row_inverted_matrix(D1)
    display_row_inverted_matrix(D2)
    
    W1 = eval_cummuled_distance_matrix(D1, 4)
    W2= eval_cummuled_distance_matrix(D2, 4)
    
    display_row_inverted_matrix(W1)
    display_row_inverted_matrix(W2)
