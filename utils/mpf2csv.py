#! /usr/bin/env python3

import sys
import struct
import collections
import os.path

MAGIC_GUID = '943737D5-AC41-49AE-AD6C-54E4C781B2F4'

do_debug = False

def debug(msg):
    if do_debug:
        print(msg)

Fixture = collections.namedtuple("Fixture", ['x', 'y', 'universe', 'channel', 'name'])

class PatchFile(object):
    def __init__(self, filename):
        fh = open(filename, "rb")
        self.data = fh.read()
        self.pos = 0
        self.fixtures = []

    def _check_eof(self, n):
        if self.pos + n > len(self.data):
            raise EOFError

    def read_bytes(self, n):
        self._check_eof(n)
        val = self.data[self.pos:self.pos + n]
        self.pos += n
        return val

    def read_int(self, fmt):
        n = struct.calcsize(fmt)
        self._check_eof(n)
        val = struct.unpack_from(fmt, self.data, self.pos)
        self.pos += n
        return val[0]

    def read_8(self):
        return self.read_int("<B")

    def read_16(self):
        return self.read_int("<H")

    def read_32(self):
        return self.read_int("<I")

    def read_64(self):
        return self.read_int("<Q")

    def read_ascii(self, n):
        self._check_eof(n)
        val = self.data[self.pos:self.pos + n]
        self.pos += n
        return val.decode("ascii", errors="replace")

    def read_pstring(self):
        n = self.read_8()
        return self.read_ascii(n)

    def read_nstring(self):
        n = self.read_16()
        return self.read_ascii(n)

    def expect_8(self, val):
        seen = self.read_8()
        if seen != val:
            raise Exception("Expected 0x%x got 0x%x" % (val, seen))

    def expect_16(self, val):
        seen = self.read_16()
        if seen != val:
            raise Exception("Expected 0x%x got 0x%x" % (val, seen))

    def expect_32(self, val):
        seen = self.read_32()
        if seen != val:
            raise Exception("Expected 0x%x got 0x%x" % (val, seen))

    def decode_block(self):
        debug("Block at 0x%x" % self.pos)
        btype = self.read_32()
        guid = self.read_pstring()
        if guid != MAGIC_GUID:
            raise Exception("Incorrect GUID: '%s'" % guid)
        if btype == 1:
            self.read_bytes(0x14) # ???
            self.expect_16(0xffff)
            self.expect_16(1)
            s = self.read_nstring()
            self.expect_8(1)
        elif btype == 5:
            protocol = self.read_pstring()
            self.expect_32(3)
            self.expect_32(1)
            self.expect_32(1)
            self.expect_32(3)
            self.expect_32(0)
            self.expect_32(0x1ff)
            shortname = self.read_pstring()
            debug(shortname)
            manufacturer = self.read_pstring()
            debug(manufacturer)
            fixture = self.read_pstring()
            debug(fixture)
            self.expect_16(0)
            self.expect_16(3)
            for channel in range(3):
                d7 = self.read_16()
                if d7 == 0xffff:
                    num_str = self.read_16()
                    for _ in range(num_str):
                        self.read_nstring()
                elif d7 == 0x8003:
                    pass
                else:
                    raise Exception("Unkown block magix 0%x" % d7)
                self.expect_32(3)
                self.expect_32(channel)
                self.expect_8(0)
                self.expect_16(0)
                self.expect_32(0xff)
                self.expect_32(0)
                self.expect_32(0)
                self.expect_32(channel)
                chan_name = self.read_pstring()
                debug(chan_name)
                self.expect_16(0)
            self.expect_32(2)
            dmx_channel = self.read_32()
            dmx_universe = self.read_32()
            rotation = self.read_32()
            pixel_x = self.read_32()
            pixel_y = self.read_32()
            debug("x=%d y=%d dmx=%d/%d" % (pixel_x, pixel_y, dmx_universe, dmx_channel))
            self.expect_32(0)
            self.expect_8(0)
            try:
                self.expect_16(0x8001)
                self.expect_8(1)
            except EOFError:
                pass
            f = Fixture(pixel_x, pixel_y, dmx_universe, dmx_channel, shortname)
            self.fixtures.append(f)
        else:
            raise Exeption("Unkown block type 0x%x" % btype)

    def decode(self):
        try:
            ver = self.read_32()
            if ver != 2:
                raise Exception("Bad file version: 0x%x" % ver)
            patch_length = self.read_64() + 12
            if patch_length != len(self.data):
                raise Exception("Bad file length (expected %d got %d)" % \
                        (len(self.data), patch_length))
            self.read_bytes(0x11) # ???
            while self.pos != patch_length:
                self.decode_block()
                debug("0x%x/0x%x" % (self.pos, patch_length))
        except:
            debug("At address 0x%x" % self.pos)
            raise
    def write_csv(self, f):
        f.write(b"X,Y,Universe,Channel,Name\n")
        for led in self.fixtures:
            f.write(('%d,%d,%d,%d,"%s"\n'%(led.x, led.y, led.universe, led.channel, led.name)).encode('ascii'))

        

def main():

    pf = PatchFile(os.path.join('..','Resources', 'mapped.mpf'))
    pf.decode()

    f = open(os.path.join('..', 'Resources', 'pixels_mapped.csv'), 'wb')
    pf.write_csv(f)
    f.close()

if __name__ == "__main__":
    main()
