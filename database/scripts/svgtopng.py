#!/usr/bin/python3

import sys
from os import remove
from subprocess import Popen, PIPE, call
from io import BytesIO
from gi import require_version
use_inkscape = False
disable_svg2png = False
try:
    require_version('Rsvg', '2.0')
    from cairosvg import svg2png
    from gi.repository import Rsvg
    import cairo
except (ImportError, AttributeError, ValueError):
    ink_flag = call(['which', 'inkscape'], stdout=PIPE, stderr=PIPE)
    if ink_flag == 0:
        use_inkscape = True
    else:
        disable_svg2png = True


def convert_svg2png(infile, outfile, icon_size=None):
    """
        Converts svg files to png using Cairosvg or Inkscape
        @file_path : String; the svg file absolute path
        @dest_path : String; the png file absolute path
    """
    if not disable_svg2png:
        if use_inkscape:
            if icon_size:
                p = Popen(["inkscape", "-z", "-f", infile, "-e", outfile,
                           "-w", str(icon_size), "-h", str(icon_size)],
                          stdout=PIPE, stderr=PIPE)
            else:
                p = Popen(["inkscape", "-z", "-f", infile, "-e", outfile],
                          stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
        else:
            if icon_size:
                handle = Rsvg.Handle()
                svg = handle.new_from_file(infile)
                dim = svg.get_dimensions()

                img = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, icon_size, icon_size)
                ctx = cairo.Context(img)
                ctx.scale(icon_size / dim.width, icon_size / dim.height)
                svg.render_cairo(ctx)

                png_io = BytesIO()
                img.write_to_png(png_io)
                with open(outfile, 'wb') as fout:
                    fout.write(png_io.getvalue())
                svg.close()
                png_io.close()
                img.finish()
            else:
                with open(infile, "r") as content_file:
                    svg = content_file.read()
                fout = open(outfile, "wb")
                svg2png(bytestring=bytes(svg, "UTF-8"), write_to=fout)
                fout.close()


def convert_svg2bin(infile):
    """
        Converts svg files to binary in memory using Cairosvg or inkscape
        @file_path : String; the svg file absolute path
    """
    if not disable_svg2png:
        if use_inkscape:
            p = Popen(["inkscape", "-z", "-f", infile, "-e",
                       "/tmp/hardcode.png"],
                      stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            with open('/tmp/hardcode.png', 'rb') as temppng:
                ret = temppng.read()
            remove('/tmp/hardcode.png')
            return ret
        else:
            with open(infile, "r") as content_file:
                svg = content_file.read()
            return svg2png(bytestring=bytes(svg, "UTF-8"))


def is_svg_enabled():
    global disable_svg2png
    return not disable_svg2png

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    convert_svg2png(infile, outfile)
