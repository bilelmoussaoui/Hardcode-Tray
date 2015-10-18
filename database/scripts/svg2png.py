#!/usr/bin/python3

from subprocess import Popen, PIPE
import sys

try:
    from cairosvg import svg2png
    use_inkscape = True
except ImportError:
    use_inkscape = True


origfile = sys.argv[1]
symlfile = sys.argv[2]

if use_inkscape:
    p = Popen(["inkscape", "-f" ,origfile, "-e " ,symlfile], stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
else:
    with open(origfile, "r") as content_file:
        svg = content_file.read()
    fout = open(symlfile, "wb")
    svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
    fout.close()
