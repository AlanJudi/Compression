import math
import numpy as np
from golomb_coding import golomb_coding



def Ricer(S, k):
    ''' Does Rice Encoding'''
    
    
    M = 2**k;
    riced = []
    for i in S:
        sign = "0b"
        if(i < 0):
            sign = "-0b"
            
        unsigned_b = golomb_coding(abs(int(i)), M)
        signed_b = sign + unsigned_b
        riced.append(int(signed_b,2))
        
            
             
        
        
    return np.asarray(riced, dtype=np.int8)


    
        
      



    
    
        