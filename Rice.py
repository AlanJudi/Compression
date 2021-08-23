import math
import numpy

def Ricer(S, k):
    if(S > 64 or S < -64):
        return bin(S)
    
    M = 2**k;
    R1 = S & (M -1)
    R2 = S >> k

    
    if R2 < 0:
        R2 = "-0b" + IntToUnary(numpy.abs(R2))
    else :
        R2 = "0b" + IntToUnary(numpy.abs(R2))
        
    result = R2 + bin(R1)[2:2+k]
    return result

def IntToUnary(n):
    A = []  
    for i in range(n):
        A.append(1)

    A.append(0)
    B = [str(k) for k in A]
    return "".join(B)
    
    
        