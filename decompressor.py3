from os import X_OK
import pathlib
import sys
from BitOut import BitInputStream
from Reader import *
from Rice import Ricer
import numpy as np
import soundfile as sf
from bitstream import BitStream
from golomb_coding import golomb_coding
import pickle
import struct
import math
import Predictor as predictor

def main(argv):
    if len(argv) != 3:
        sys.exit(f"Usage: python {argv[0]} Sound1_Enc.ex2 Sound1_Dec.wav.wav")
    with BitInputStream(pathlib.Path(argv[1]).open("rb")) as inp:
        with pathlib.Path(argv[2]).open("wb") as out:
            decode_file(inp, out)
    
    
                
def decode_file(inp, out):
    
    # Handle FLAC header and metadata blocks
    if inp.readUint(32) != 0x664C6143:
        raise ValueError("Invalid magic string")


    samplerate = None
    last = False
    while not last:
        last = inp.readUint(1) != 0
        type = inp.readUint(7)
        length = inp.readUint(24)
        if type == 0:  # Stream info block
            inp.readUint(16)
            inp.readUint(16)
            inp.readUint(24)
            inp.readUint(24)
            samplerate = inp.readUint(20)
            numchannels = inp.readUint(3) + 1
            sampledepth = inp.readUint(5) + 1
            numsamples = inp.readUint(36)
            inp.readUint(128)
        else:
            for i in range(length):
                inp.readUint(8)
    if samplerate is None:
        raise ValueError("Stream info metadata block absent")
    if sampledepth % 8 != 0:
        raise RuntimeError("Sample depth not supported")
	
    # Start writing WAV file headers
    sampledatalen = numsamples * numchannels * (sampledepth // 8)
    out.write(b"RIFF")
    out.write(struct.pack("<I", sampledatalen + 36))
    out.write(b"WAVE")
    out.write(b"fmt ")
    out.write(struct.pack("<IHHIIHH", 16, 0x0001, numchannels, samplerate,
        samplerate * numchannels * (sampledepth // 8), numchannels * (sampledepth // 8), sampledepth))
    out.write(b"data")
    out.write(struct.pack("<I", sampledatalen))
    
    # Decode FLAC audio frames and write raw samples
    while decode_frame(inp, numchannels, sampledepth, out):
        pass
    
def decode_frame(inp, numchannels, sampledepth, out):
    # Read a ton of header fields, and ignore most of them
	temp = inp.read_byte()
 
	if temp == -1:
		return False
	sync = temp << 6 | inp.readUint(6)
	if sync != 0x3FFE:
		raise ValueError("Sync code expected")
	
	inp.readUint(1)
	inp.readUint(1)
	blocksizecode = inp.readUint(4)
	sampleratecode = inp.readUint(4)
	chanasgn = inp.readUint(4)
	inp.readUint(3)
	inp.readUint(1)
	
	temp = inp.readUint(8)
	while temp >= 0b11000000:
		inp.readUint(8)
		temp = (temp << 1) & 0xFF
	
	if blocksizecode == 1:
		blocksize = 192
	elif 2 <= blocksizecode <= 5:
		blocksize = 576 << blocksizecode - 2
	elif blocksizecode == 6:
		blocksize = inp.readUint(8) + 1
	elif blocksizecode == 7:
		blocksize = inp.readUint(16) + 1
	elif 8 <= blocksizecode <= 15:
		blocksize = 256 << (blocksizecode - 8)
	
	if sampleratecode == 12:
		inp.readUint(8)
	elif sampleratecode in (13, 14):
		inp.readUint(16)
	
	inp.readUint(8)
	
	# Decode each channel's subframe, then skip footer
	samples = decode_subframes(inp, blocksize, sampledepth, chanasgn)
	inp.align_to_byte()
	inp.readUint(16)
	
	
def decode_subframes(inp, blocksize, sampledepth, chanasgn):
    if 0 <= chanasgn <= 7:
	    return [decode_subframe(inp, blocksize, sampledepth) for _ in range(chanasgn + 1)]
    elif 8 <= chanasgn <= 10:
        temp0 = decode_subframe(inp, blocksize, sampledepth + (1 if (chanasgn == 9) else 0))
        temp1 = decode_subframe(inp, blocksize, sampledepth + (0 if (chanasgn == 9) else 1))
        if chanasgn == 8:
            for i in range(blocksize):
                temp1[i] = temp0[i] - temp1[i]
        elif chanasgn == 9:
            for i in range(blocksize):
                temp0[i] += temp1[i]
        elif chanasgn == 10:
            for i in range(blocksize):
                side = temp1[i]
                right = temp0[i] - (side >> 1)
                temp1[i] = right
                temp0[i] = right + side
        return [temp0, temp1]
    else:
	    raise ValueError("Reserved channel assignment")
 
def decode_subframe(inp, blocksize, sampledepth):

    inp.readUint(1)
    type = inp.readUint(6)
    shift = inp.readUint(1)
    
    result = [inp.read_signed_int(8) for _ in range(blocksize + 14)]
    print(result)

    
    
            
if __name__ == "__main__":
    main(sys.argv)