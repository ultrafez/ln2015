__author__ = 'ajtag'


import csv
import xml.etree.ElementTree as ET
import os.path
import math
from collections import namedtuple

white = 255,255,255

Lamp = namedtuple("Lamp", ["x", "y", 'name', 'dmx', 'channel'])

def parse_imagemask_svg(x, y, scale, x_offset = 19, y_offset = 0):
        tree = ET.parse('../Resources/LS-TRIN-0023 East Mall.svg')
        root = tree.getroot()
        groups = root.findall('{http://www.w3.org/2000/svg}g')

        mnlx, mxlx, mnly, mxly = None, None, None, None

        tmplamps = []

        for g in groups:
            paths = g.findall('{http://www.w3.org/2000/svg}path')

            if mnlx is None:
                mnlx = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                mxlx = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                mnly = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])
                mxly = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])

            for p in paths:
                lampx = float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                lampy = float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])

                mnlx = min(mnlx, lampx)
                mxlx = max(mxlx, lampx)
                mnly = min(mnly, lampy)
                mxly = max(mxly, lampy)

                tmplamps.append((lampx, lampy))

        return [(x_offset + ((lamp[0] - mnlx)/(mxlx - mnlx) * x * scale), y_offset + ((lamp[1] - mnly)/(mxly - mnly) * y * scale)) for lamp in tmplamps]



f = open(os.path.join('..', 'Resources', 'pixels.csv'))
ch = csv.DictReader(f)

madrixlamps = [Lamp(i['X'], i['Y'], i['Name'], i['Universe'], i['Channel']) for i in ch]
f.close()



scale = 1

# missing light to the left of 19px in madrix lamps
planlamps = [Lamp(i[0], i[1], None, None, None) for i in parse_imagemask_svg(132, 70, scale)]



for i in  enumerate(zip(madrixlamps, planlamps)):
    print(i)

def distance(l1, l2):
    return math.sqrt(pow(l1.x - l2.x, 2) + pow(l1.y - l2.y, 2, 2))









