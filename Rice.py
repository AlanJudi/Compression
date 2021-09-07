import math
import numpy as np
import bitstream


def Ricer_encode(S, k, signed):
    ''' Does Rice Encoding'''
    
    
    M = 2**k;
    n = int(S)
    
    
    if signed and n > 0:
        n = 2*n
    elif signed and n < 0:
        n = 2 * abs(n) - 1
    
    r = encode_golomb(abs(n), M, signed)
    
      
    return r

def min_binary(s):
    '''Removes leading zeros'''
    bits = s.lstrip("0") 
    
    if not bits:
        bits = '0'
        
    return bits

def remainder_truncate(r, k):
    '''Truncates remainder'''
    rem = bin(r)
    return rem.split('b')[1].zfill(k)

def encode_golomb(n, M, signed):
    '''Returns a string value of bits'''

    
    q1 = (n // M)
    q = math.floor(q1)
    
    unary_code = unary(q)
    
    
    k1 = math.log(M, 2)
    k = math.ceil(k1)
    
    r = n % M
    
    
    #truncate remainder
    r1 = remainder_truncate(r, k)
    result = unary_code + r1
        
    return result
        


def unary(q):
    '''Converts int to unary representation'''
    A = []
  
    for i in range(q):
        A.append(1)
      
    A.append(0)
  
    B = [str(k) for k in A]
  
    C = "".join(B)
    
    
    return C





def Ricer_decode(S, k, signed):
    '''Reverses rice coding'''
    '''Accepts an array of bit strings'''
    M = 2**k;
        
    r = decode_rice(S, M, signed)

        
    return r

def decode_rice(S, m, signed):
    ''' decode rice bit string'''
    ''' Returns an decoded integer'''

    
    code = [str(i) for i in S]

    
    k1 = math.log(m, 2)
    k = math.ceil(k1)
    q = 0
    
    for i in range(len(code)-k):
        if int(code[i]) == 1:
            q = q + 1
        else:
            break
            
    for i in range(q):
        code.pop(0)
        
    code1 = [str(i) for i in code]
    code2 = "".join(code1)
    
    n = 0
    r1 = []
    
    for i in range(len(code)):
        r1.append(code[i])
        
    r2 = [str(i) for i in r1]
    r3 = "".join(r2)
    r = int(r3, 2)

    n = q * m + r

    ## adjust for +ve and negative values
    if n % 2 == 1 and signed:
        n = (n+1)/2*(-1)
    elif n%2 == 0 and signed:
        n = n/2


    return int(n)



class rice_tag(object):
    '''Rice codec tag type'''
    def __init__(self, b, signed):
        self.b = b 
        self.signed = signed


def write_factory(instance):
    '''Writes rice signed stream'''
    b = instance.b
    signed = instance.signed
    m = 2**instance.b
    def write_uint(stream, data):
        if isinstance(data, list) or isinstance(data, np.ndarray):

            for i in data:
                write_uint(stream, i)
        else:
            integer = int(data) 
            
            rice = Ricer_encode(integer, b, signed = signed)
            bools = [i=='1' for i in rice] 
            stream.write(bools, bool)
            
                    
    return write_uint

def read_uint_factory(instance):
    '''Reads rice signed stream'''
    signed = instance.signed
    b = instance.b
    m = 2**instance.b
    def read_uint(stream, n=None):
        if n is None:
            end = False
            start = True
            have_quotient = False
            bools = []
            while not end:
                try:
                    val = stream.read(bool)
                    
                    
                    
                    if (val and not have_quotient):
                        bools.append(val)
                        start = False
                    elif (not val and not have_quotient):
                        bools.append(val)
                        have_quotient = True
                        
                    if(have_quotient):
                        bits = b
                        
                        if b == 0:
                            bits = bits + 1
                            
                        for i in range(bits):
                            bools.append(stream.read(bool)) 
                        end = True
                              
                
                except:
                    return None
                
                
  
         
            # initialization of string to ""
            S = "".join([str(int(i)) for i in bools])  
            r = Ricer_decode(S, b, signed =signed)

            return r
 
        else:
            integers = [read_uint(stream) for i in range(n)]
            return integers
    return read_uint





    
        
      



    
    
        