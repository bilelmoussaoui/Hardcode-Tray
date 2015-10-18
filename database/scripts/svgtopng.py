#!/usr/bin/python3

import sys
from os import symlink, chown, getenv, remove
from subprocess import Popen, PIPE

try:
    from cairosvg import svg2png
    use_inkscape = False
except ImportError:
    ink_flag = call(['which', 'inkscape'])
    if ink_flag == 0:
        use_inkscape = True
    else:
        exit("You need either a working python-cairosvg installation or inkscape installed. Exiting.")

def convert_svg2png(infile, outfile):
    """
        Converts svg files to png using Cairosvg or Inkscape
        @file_path : String; the svg file absolute path
        @dest_path : String; the png file absolute path
    """
    if use_inkscape:
        p = Popen(["inkscape", "-f" ,infile, "-e " ,outfile], stdout=PIPE, stderr=PIPE)
    else:
        with open(infile, "r") as content_file:
            svg = content_file.read()
        fout = open(outfile, "wb")
        svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
        fout.close()



if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    convert_svg2png(infile, outfile)
