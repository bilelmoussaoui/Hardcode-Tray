#!/usr/bin/python3

from cairosvg import svg2png
import sys

origfile = sys.argv[1]
symlfile = sys.argv[2]

with open(origfile, "r") as content_file:
    svg = content_file.read()
fout = open(symlfile, "wb")
svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
fout.close()
