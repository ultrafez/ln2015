import struct
import os.path

__author__ = 'admin'

#pf = open(os.path.join('..', 'Resources', 'revised_patch.mpf', 'wb'))

fh = open(os.path.join('..', 'Resources', 'test_patch2.mpf'), 'rb')
tp = fh.read()
fh.close()

def parse_struct_type(file_position):
    global tp
    #print(struct.unpack_from('<4B', tp, file_position), file_position)
    if struct.unpack_from('<4B', tp, file_position)[-2] != 0:
        file_position += 3

    #print(struct.unpack_from('<4B', tp, file_position), file_position)

    structtype_fmt = '<I'
    st = struct.unpack_from(structtype_fmt, tp, file_position)
    return st[0], file_position + struct.calcsize(structtype_fmt)

def parse_string(ptr, length=None):
    global tp
    rb = tp
    if len is None:
        strlen = rb[ptr:].find(0x03)
    else:
        strlen = length
    title = struct.unpack_from('<{}c'.format(strlen), rb, ptr)
    return title, ptr + strlen

def parse_string_dyn(ptr, fmt='<B'):
    global tp
    strlen = struct.unpack_from(fmt, tp, ptr)[0]
    return parse_string( ptr+struct.calcsize(fmt), strlen), strlen+1

def parse_fixture(ptr):
    global tp
    fixture_fmt = '<37c'

    pos = 37
    x, y = parse_string_dyn(ptr + pos)
   #print(x)
    pos += y

   #print(struct.unpack_from('<IIIIII', tp, ptr + pos))
    pos += struct.calcsize('<IIIIII')

    x, y = parse_string_dyn( ptr + pos)
    pos += y
   #print(x)

    x, y = parse_string_dyn(ptr + pos)
    pos += y
   #print(x)

    x, y = parse_string_dyn(ptr + pos)
    pos += y
   #print(x)

   #print(struct.unpack_from('<4H', tp, ptr + pos))
    pos += struct.calcsize('<4H')

    x, y = parse_string_dyn(ptr + pos, '<H')
    pos += y
   #print(x)

    # padding
   #print(16-(16%y), y, 16%y)

    pos += (16 % y)

   #print(struct.unpack_from('<6I', tp, ptr + pos))
    pos += struct.calcsize('<6I')

    x, y = parse_string_dyn(ptr + pos, '<B')
    pos += y
   #print(x)


   #print(struct.unpack_from('<31c', tp, ptr + pos))
    pos += struct.calcsize('<31c')

    x, y = parse_string_dyn( ptr + pos, '<B')
    pos += y
   #print(x)

   #print(struct.unpack_from('<31c', tp, ptr + pos))
    pos += struct.calcsize('<31c')

    x, y = parse_string_dyn( ptr + pos, '<B')
    pos += y
    try:
        _, _, channel, universe, _, x, y, flip, rotation = struct.unpack_from('<H I I I I I I I B', tp, ptr + pos)

        #print( channel, universe, x, y, flip, rotation)
        print( channel, universe, x+1, y+1)
        pos += struct.calcsize('<H I I I I I I I c')

    except struct.error:
       #print(len(tp) - (ptr+pos))
        pass
    return '', ptr + pos


def parse_dmx(ptr):
    global tp
    dmxunit_fmt = '<37c 14H 14c'
    return '', ptr + struct.calcsize(dmxunit_fmt)


file_position = 0
format_str = {'1': parse_dmx, '5': parse_fixture}

header_fmt = '<3I c H I 10c'
version, length, *_ = struct.unpack_from(header_fmt, tp)

print(version, length)
file_position += struct.calcsize(header_fmt)
i = 0

while file_position < len(tp):

   #print('loop', i, hex(file_position))
    i += 1
    struct_start = file_position

    struct_type, file_position = parse_struct_type(file_position)

   #print(struct_type, struct_start)

    parsefxn = format_str.get(str(struct_type))
    if parsefxn is None:
        raise ValueError('no parser for struct {}'.format(struct_type))

    struct_data, file_position = parsefxn(file_position)
   #print('***\n\n\n***')
