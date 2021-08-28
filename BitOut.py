class BitOutputStream:

    def __init__(self, out):
        self.out = out
        self.bitbuffer = 0
        self.bitbufferlen = 0
        self.reset_crcs()
        self.CRC8_TABLE = []
        self.CRC16_TABLE = []
        self.Initialize_CRC()
        self.prederr = []

    def reset_crcs(self):
        self.crc8 = 0
        self.crc16 = 0

    def Initialize_CRC(self):
        for i in range(256):
            temp8 = i
            temp16 = i << 8
            for _ in range(8):
                temp8 = (temp8 << 1) ^ ((temp8 >> 7) * 0x107)
                temp16 = (temp16 << 1) ^ ((temp16 >> 15) * 0x18005)
            self.CRC8_TABLE.append(temp8)
            self.CRC16_TABLE.append(temp16)

    def align_to_byte(self):
        self.writeInt((-self.bitbufferlen) % 8, 0)
        
    def write(self, val):
        self.out.write(val)

    def writeInt(self, n, val):
        self.bitbuffer <<= n
        self.bitbuffer |= val & ((1 << n) - 1)
        self.bitbufferlen += n
        while self.bitbufferlen >= 8:
            self.bitbufferlen -= 8
            b = (self.bitbuffer >> self.bitbufferlen) & 0xFF
            self.out.write(bytes((b,)))
            self.crc8 = self.CRC8_TABLE[self.crc8 ^ b]
            self.crc16 = self.CRC16_TABLE[(self.crc16 >> 8) ^ b] ^ ((self.crc16 & 0xFF) << 8)
        self.bitbuffer &= (1 << self.bitbufferlen) - 1


    def close(self):
        self.out.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        
class BitInputStream:
    def __init__(self, inp):
        self.inp = inp
        self.bitbuffer = 0
        self.bitbufferlen = 0

    def align_to_byte(self):
        self.bitbufferlen -= self.bitbufferlen % 8

    def read_byte(self):
        if self.bitbufferlen >= 8:
            return self.readUint(8)
        else:
            result = self.inp.read(1)
            if len(result) == 0:
                return -1
            return result[0]

    def readUint(self, n):
        while self.bitbufferlen < n:
            temp = self.inp.read(1)
            if len(temp) == 0:
                raise EOFError()
            self.bitbuffer = (self.bitbuffer << 8) | temp[0]
            self.bitbufferlen += 8
        self.bitbufferlen -= n
        result = (self.bitbuffer >> self.bitbufferlen) & ((1 << n) - 1)
        self.bitbuffer &= (1 << self.bitbufferlen) - 1
        return result

    def read_signed_int(self, n):
        temp = self.readUint(n)
        temp -= (temp >> (n - 1)) << n
        return temp

    def read_rice_signed_int(self, param):
        val = 0
        while self.readUint(1) == 0:
            val += 1
        val = (val << param) | self.readUint(param)
        return (val >> 1) ^ -(val & 1)

    def close(self):
        self.inp.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

