# -*- encoding : utf-8 -*-

import numpy as np
import matplotlib.pylab as plt


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
    """Evaluate the cummuled distance matrix G from a distance matrix D
    
    Parameter
    D -- distance matrix
    r -- warping windows
    """
    
    #Use warping or not
    warp = False
    if r is not None:
        warp = True
    
    nn, mm = np.shape(D)
    G = np.zeros((nn, mm))
    
    #REM : We will use there a Symetric DTW wit warping windows and no slope constraint
    
    for i in range(nn):
        for j in range(mm):
            #Initialisation
            if i == j == 0:
                G[i, j] = D[0, 0]
            else:
                if warp and warping_window(i, j, r):
                    continue;
                d = []
                if i > 0:
                    d.append(G[i-1, j] + D[i, j])
                if i > 0 and j > 0:
                    d.append(G[i-1, j-1] + 2*D[i, j])
                if j > 0:
                    d.append(G[i, j-1] + D[i,j])
                G[i,j] = min(d)
    return G
    
def dtw(A, s, debug = False):
    """Dtw algorithm to find from which sequence in the dict A the sequence s 
    is the closest.
    """
    if debug:
        print("------------------------")
        print("----------DTW-----------")
        
    d = []
    for ref_seq_name in A.keys():
        
        ref_seq = A[ref_seq_name]
        D = eval_distance_matrix(ref_seq, s)
        
        G = eval_cummuled_distance_matrix(D)
        
        
        nn, mm = np.shape(G)
        
        
        time_normalized_dist = G[nn-1, mm-1] / (mm+nn)
        
        d.append((ref_seq_name, time_normalized_dist))
        
        if debug:
            print(ref_seq_name)
            print("distance_matrix : ")
            print(D)
            
            print("cummuled_distance_matrix : ")
            print(G)
            plt.figure()
            plt.imshow(G)
            plt.title("%s, distance = %s"%(ref_seq_name,time_normalized_dist ))
            print("time_normalized_dist = %s"%(time_normalized_dist))
        
    closest_seq = min(d, key=lambda x: x[1])[0]
    
    if debug:
        print("The closest seq is : %s!"%closest_seq)
    
    return closest_seq
        
        
        
    
	
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
    
    W1 = eval_cummuled_distance_matrix(D1)
    W2= eval_cummuled_distance_matrix(D2)
    
    print(W1)
    print(W2)
    
    nn = 100
    rand_seq = np.random.randn(nn)
    lin_seq = np.linspace(0, nn, nn)
    
    A = {"s2":s2, "s3":s3}
    B = {"rand_seq":rand_seq, "lin_seq":lin_seq}
    x1 = np.linspace(0, 100, 100)  
    x2 = np.concatenate((np.linspace(0, 100, 50), np.linspace(100, 0, 50)))
    y = np.linspace(0, 100, 50)  
    C = {"x1":x1, "x2":x2}
    closest_seq = dtw(C, y, debug = True)
    
#    plt.figure()
#    x1 = np.linspace(0, 100, 100)  
#    x2 = np.concatenate((np.linspace(0, 100, 50), np.linspace(100, 0, 50)))
#    y = np.linspace(0, 100, 50) 
#    plt.subplot(311)
#    plt.plot(x1)
#    plt.title("x1")
#    plt.subplot(312)
#    plt.plot(x2)
#    plt.title("x2")
#    plt.subplot(313)
#    plt.plot(y)
#    plt.title("y")
    
