# -*- encoding : utf-8 -*-

import m_log as Log

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
    
def eval_time_normalized_dist(x, y, debug = False):
        D = eval_distance_matrix(x, y)
        G = eval_cummuled_distance_matrix(D)
        nn, mm = np.shape(G)
        time_normalized_dist = G[nn-1, mm-1] / (mm+nn)
        
        if debug:
            print("distance_matrix : ")
            print(D)
            print("cummuled_distance_matrix : ")
            print(G)
            plt.figure()
            plt.imshow(G)
            
        
        return time_normalized_dist
    
    
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
        time_normalized_dist = eval_time_normalized_dist(ref_seq, s, debug = True)
        
        d.append((ref_seq_name, time_normalized_dist))
        
        if debug:        
            plt.title("%s, distance = %s"%(ref_seq_name,time_normalized_dist ))
            print("time_normalized_dist = %s"%(time_normalized_dist))
        
        
        
    closest_seq = min(d, key=lambda x: x[1])[0]
    
    if debug:
        print("The closest seq is : %s!"%closest_seq)
    
    return closest_seq
    
def multi_d_dtw(A, s, debug = False):
    """DTW algorithme for multi dimensionnal time series
    """
    
    dist_list = []
    
    for ref_seq_name in A.keys():
        ref_seq = A[ref_seq_name]
        
        if debug:        
            print("seq %s : "%(ref_seq_name))
        
        d_weight_list = []
        for d in range(len(ref_seq)):
            ref_seq_d = ref_seq[d]
            s_d = s[d]
            
            time_normalized_dist = eval_time_normalized_dist(ref_seq_d, s_d)
            d_weight_list.append(time_normalized_dist)
            
            if debug:
                print("Dim %s : dist = %s"%(d, time_normalized_dist))
            
        dimentionnal_time_normalized_dist = sum(d_weight_list)
        
        if debug:        
                print("dimentionnal_dist : %s"%(dimentionnal_time_normalized_dist))
        
        dist_list.append((ref_seq_name, dimentionnal_time_normalized_dist))
        
    closest_seq = min(dist_list, key=lambda x: x[1])[0]
    
    if debug:
        print("The closest seq is : %s!"%closest_seq)
    
def multi_d_multi_key_dtw(A, s, debug = False):
    """
    
    TODO : Brut force
    """
    
    dist_list = []
    
    for ref_seq_name in A.keys():
        ref_seq_list = A[ref_seq_name]
        Log.d("[multi_d_multi_key_dtw]", "ref_gesture_name : %s"%ref_seq_name, True)
        
        if len(ref_seq_list) == 0:
            Log.d("[multi_d_multi_key_dtw]", "ref_seq_list is empty, no match possible", True)
            return None
        
        if debug:        
            print("seq %s : "%(ref_seq_name))
            
        
        
        # For each ref seq        
        i=0
        seq_weight_list = []
        for ref_seq in ref_seq_list:
            
            if debug:        
                print("ref_seq %s : "%(i))
        
            # For each dimention            
            d_weight_list = []
            for d in range(len(ref_seq)):
                ref_seq_d = ref_seq[d]
                s_d = s[d]
                
                time_normalized_dist = eval_time_normalized_dist(ref_seq_d, s_d)
                d_weight_list.append(time_normalized_dist)
                
                if debug:
                    print("Dim %s : dist = %s"%(d, time_normalized_dist))
                    
            
            # We take the sum all all the dimention
            multi_d_time_normalized_dist = sum(d_weight_list)
            
            seq_weight_list.append(multi_d_time_normalized_dist)
            
            if debug:        
                print("dimentionnal_dist : %s"%(multi_d_time_normalized_dist))
            Log.d("[multi_d_multi_key_dtw]", "ref gesture n°%s : dist = %s\n"%(i, multi_d_time_normalized_dist), True)
            i+=1
                    
            
        # We take the average min the different ref seq           
        ref_seq_list_weight = min(seq_weight_list)
        
        if debug:        
            print("ref_seq_list_weight : %s"%(ref_seq_list_weight))
        
        dist_list.append((ref_seq_name, ref_seq_list_weight))
        
        
    closest_seq = min(dist_list, key=lambda x: x[1])[0]
    
    if debug:
        print("The closest seq is : %s!"%closest_seq)
        
    return closest_seq
    
            
def display_row_inverted_matrix(D):
    """Display the distance matrix with the origin in the bottom left corner.
	"""
    D = np.flipud(D)
    print(D)
    
	
if __name__ == "__main__":
    
    test = 4
    
    if test == 1:
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
    
    if test == 2:
        plt.figure()
        x1 = np.linspace(0, 100, 100)  
        x2 = np.concatenate((np.linspace(0, 100, 50), np.linspace(100, 0, 50)))
        y = np.linspace(0, 100, 50) 
        plt.subplot(311)
        plt.plot(x1)
        plt.title("x1")
        plt.subplot(312)
        plt.plot(x2)
        plt.title("x2")
        plt.subplot(313)
        plt.plot(y)
        plt.title("y")
        
    #Multi dim DTW
    if test == 3:
        
        x_d1 = np.linspace(0, 100, 100)
        x_d2 = np.linspace(0, 100, 100)
        x_d3 = np.linspace(0, 100, 100)
    
        y_d1 = np.linspace(100, 0, 100)
        y_d2 = np.linspace(100, 0, 100)
        y_d3 = np.linspace(100, 0, 100)
        
        x = np.array([x_d1, x_d2, x_d3])
        y = np.array([y_d1, y_d2, y_d3])
        
        A = {"x" : x, "y" : y}
        
        
        multi_d_dtw(A, x,  debug=True) 
        
    #Multi dim multi key DTW
    if test == 4:
        
        x1_d1 = np.linspace(0, 100, 100)
        x1_d2 = np.linspace(0, 100, 100)
        x1_d3 = np.linspace(0, 100, 100)
        
        x2_d1 = np.linspace(0, 200, 100)
        x2_d2 = np.linspace(0, 200, 100)
        x2_d3 = np.linspace(0, 200, 100)
    
        y1_d1 = np.linspace(100, 0, 100)
        y1_d2 = np.linspace(100, 0, 100)
        y1_d3 = np.linspace(100, 0, 100)
        
        y2_d1 = np.linspace(100, 0, 100)
        y2_d2 = np.linspace(200, 0, 100)
        y2_d3 = np.linspace(200, 0, 100)
        
        x1 = np.array([x1_d1, x1_d2, x1_d3])
        x2 = np.array([x2_d1, x2_d2, x2_d3])
        y1 = np.array([y1_d1, y1_d2, y1_d3])
        y2 = np.array([y2_d1, y2_d2, y2_d3])
        
        x = np.array([x1, x2])
        y = np.array([y1, y2])
        
        A = {"x" : x, "y" : y}
        
        z_d1 = np.linspace(24, 100, 50)
        z_d2 = np.linspace(0, 100, 90)
        z_d3 = np.linspace(-20, 50, 60)
        
        z = np.array([z_d1, z_d2, z_d3])
        
        
        multi_d_multi_key_dtw(A, z, debug=True) 
    
