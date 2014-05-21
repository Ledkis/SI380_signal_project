# -*- encoding : utf-8 -*-

import numpy as np


def eucl_dist(x, y):
    """Compute the euclidian distance between vector x and y.
    """
    return np.sqrt(np.sum((x-y)**2))
    


def eval_distance_matrix(s1, s2,  d_eval = lambda x,y : (x - y)**2):
    """Create the distance matrix between the time series s1 and s2 using
    the distance d_eval.
    
    Parameter
    s1 -- time serie n°1    
    s2 -- time serie n°2
    d_val -- distance between s1(i) and s2(j)
            By default : d_val(i,j) = (s1(i)-s2(j))**2
    
    """
    
    mm = s1.size
    nn = s2.size
    
    #Initialisation of the distance matrix
    D = np.zeros((mm, nn));
    
    for i in range(mm):
        for j in range(nn):
            D[i, j] = d_eval(s1[i], s2[j])
            
    return D
	
def display_distance_matrix(D):
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
    
    
    display_distance_matrix(D1)
    display_distance_matrix(D2)
