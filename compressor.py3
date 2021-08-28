from os import X_OK
import pathlib
import sys
from BitOut import BitOutputStream
from Reader import *
from Rice import Ricer
import numpy as np
import soundfile as sf
from bitstream import BitStream
from golomb_coding import golomb_coding
import struct
import math
import Predictor as predictor

#standard block size
BLOCK_SIZE = 4096

def main(argv):
    if len(argv) != 3:
        sys.exit(f"Usage: python {argv[0]} InFile.wav OutFile.flac")
    with pathlib.Path(argv[1]).open("rb") as binary_input:
        with BitOutputStream(pathlib.Path(argv[2]).open("wb")) as binary_output:
            encode_file(binary_input, binary_output)


def encode_file(binary_input, out):
    
    # Read and parse WAV file headers
    CheckFile(ReadNInput(binary_input, 4) != b"RIFF", "Invalid RIFF file header")
    ConvertToSmallInt(binary_input, 4)
    CheckFile(ReadNInput(binary_input, 4) != b"WAVE", "Invalid WAV file header")
    CheckFile(ReadNInput(binary_input, 4) != b"fmt ", "Unrecognized WAV file chunk")
    CheckFile(ConvertToSmallInt(binary_input, 4) != 16, "Unsupported WAV file type")
    CheckFile(ConvertToSmallInt(binary_input, 2) != 0x0001, "Unsupported WAV file codec")
    
    #number of channels
    numchannels = ConvertToSmallInt(binary_input, 2)
    CheckFile(not (1 <= numchannels <= 8), "Too many (or few) audio channels")
    
    #sample rate
    samplerate = ConvertToSmallInt(binary_input, 4)
    CheckFile(not (1 <= samplerate < (1 << 20)), "Sample rate too large or invalid")
    
    ConvertToSmallInt(binary_input, 4)
    ConvertToSmallInt(binary_input, 2)
    
    #sampledepth
    sampledepth = ConvertToSmallInt(binary_input, 2)
    
    CheckFile(sampledepth not in (8, 16, 24, 32), "Unsupported sample depth")
    CheckFile(ReadNInput(binary_input, 4) != b"data", "Unrecognized WAV file chunk")
    
    sampledatalen = ConvertToSmallInt(binary_input, 4)
    CheckFile(sampledatalen <= 0 or sampledatalen % (numchannels * (sampledepth // 8)) != 0, "Invalid length of audio sample data")

    # Start writing FLAC file header and stream info metadata block
    out.writeInt(32, 0x664C6143)
    out.writeInt(1, 1)
    out.writeInt(7, 0)
    out.writeInt(24, 34)
    out.writeInt(16, BLOCK_SIZE)
    out.writeInt(16, BLOCK_SIZE)
    out.writeInt(24, 0)
    out.writeInt(24, 0)
    out.writeInt(20, samplerate)
    out.writeInt(3, numchannels - 1)
    out.writeInt(5, sampledepth - 1)
 
    numsamples = sampledatalen // (numchannels * (sampledepth // 8))
    
    
    out.writeInt(36, numsamples)
    for _ in range(16):
        out.writeInt(8, 0)
    
        
    numblocks = int(math.ceil(numsamples/BLOCK_SIZE))
    
  
    i = 0
    while numsamples > 0:
        blocksize = min(numsamples, BLOCK_SIZE)
        encodeFrame(binary_input, i, numchannels, sampledepth, samplerate, blocksize, out)
        numsamples -= blocksize
        i += 1
    



def encodeFrame(binary_input, frameindex, numchannels, sampledepth, samplerate, blocksize, out):
    
    #Bytes per sample
    bytespersample = sampledepth // 8
    
    #can be two channels, i.e stereo
    samples = [[] for _ in range(numchannels)]
    for _ in range(blocksize):
        for channelSamples in samples:
            val = ConvertToSmallInt(binary_input, bytespersample)
            if sampledepth == 8:
                val -= 128
            else:
                val -= (val >> (sampledepth - 1)) << sampledepth
            
            channelSamples.append(val*1.0) 
            
    out.reset_crcs()
    out.writeInt(14, 0x3FFE)
    out.writeInt(1, 0)
    out.writeInt(1, 0)
    out.writeInt(4, 7)
    out.writeInt(4, (14 if samplerate % 10 == 0 else 13))
    out.writeInt(4, numchannels - 1)
    out.writeInt(3, {8:1, 16:4, 24:6, 32:0}[sampledepth])
    out.writeInt(1, 0)
    out.writeInt(8, 0xFC | (frameindex >> 30))
    for i in range(24, -1, -6):
        out.writeInt(8, 0x80 | ((frameindex >> i) & 0x3F))
    out.writeInt(16, blocksize - 1)
    out.writeInt(16, samplerate // (10 if samplerate % 10 == 0 else 1))
    out.writeInt(8, out.crc8)
    
                    

    for i in range(len(samples)):
        ''' Encodes sub frame'''
        L = 10 #predictor
        h=np.zeros(L)
        e = predictor.nlmslosslesspredenc(samples[i],L,h)
        
        
        e = np.concatenate((e, [0,0,0,0]), axis = 0)
        
        out.writeInt(1, 0)
        out.writeInt(6, 1)  
        out.writeInt(1, 0)
        

        riced = Ricer(e, 4)
        stream = BitStream(riced, np.int8)
        prederrors=stream.read(bytes, np.floor(len(stream)/8.0))
        out.out.write(prederrors)
            
    out.align_to_byte()
    out.writeInt(16, out.crc16)
            
            
        
        
        
        
        


        
        
        
 
        
     
    
        
        
        
      
            
   
        
        
        
  
 


    
    

        

        
    
    
   
        


if __name__ == "__main__":
    main(sys.argv)
