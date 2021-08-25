import numpy as np

def nlmslosslesspreddec(e,L,h):
    xrek = np.zeros(len(e))
    for n in range(L, len(e)):
        
        xrekvec = xrek[n - L + np.arange(L)]
        
        P = np.dot(np.flipud(xrekvec), h)
        
        P = round(P)
        
        xrek[n] = e[n] + P
        h = h + 1.0* e[n]* np.flipud(xrekvec) / 1.0 + np.dot(xrekvec,xrekvec)
        
    return np.hstack((xrek[L:], np.zeros(L)))

def nlmslosslesspredenc(x,L,h):
    '''Computes the NLMS lossless predictor'''
    
    #arguments: x: input signal (mono)
    #L: Predictor lenght
    #h: starting values for the L predictor coefficients
    #returns: e, the prediction error
    x=np.hstack((np.zeros(L),x)); #make same starting conditions as decoder 
    e=np.zeros(len(x));
    for n in range(L, len(x)):
        #prediction error and filter, using the vector of reconstructed samples, 
        xrekvec=x[n-L+np.arange(L)]
        P=np.dot(np.flipud(xrekvec), h);
        #quantize and de−quantize by rounding to the nearest integer: 
        P=round(P)
        #prediction error:
        e[n]=x[n]-P
        #NLMS update:
        h = h + 1.0 * e[n] * np.flipud(xrekvec)/(0.1+np.dot(xrekvec,xrekvec))
    return e