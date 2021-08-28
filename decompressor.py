from os import X_OK
import pathlib
import sys
from BitInput import BitInputStream
from Reader import *
from Rice import Ricer
import numpy as np
import soundfile as sf
from bitstream import BitStream
import struct
import math
import Predictor as predictor

def main(argv):
    if len(argv) != 3:
        sys.exit(f"Usage: python {argv[0]} Sound1_Enc.ex2 Sound1.wav")
    with pathlib.Path(argv[1]).open("rb") as binary_input:
        with BitInputStream(pathlib.Path(argv[2]).open("wb")) as binary_output:
            decode_file(binary_input, binary_output)

def decode_file(inp, out):
    
            
if __name__ == "__main__":
    main(sys.argv)