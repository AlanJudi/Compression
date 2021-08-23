import pathlib
import sys
from BitOut import BitOutputStream
from Reader import *
from Rice import Ricer
import numpy as np
import soundfile as sf

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


    numsamples = sampledatalen // (numchannels * (sampledepth // 8))

    
    # Read raw samples and encode FLAC audio frames
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
            
            channelSamples.append(val)  
            

    for chansamples in samples:
        encode_subframe(chansamples, sampledepth, out)
	

 
def encode_subframe(samples, sampledepth, out):

    for x in samples:
        val = Ricer(x,4)
        print(val)
        
   
        

            
   
    



    
        

        
    
    
   
        


if __name__ == "__main__":
    main(sys.argv)