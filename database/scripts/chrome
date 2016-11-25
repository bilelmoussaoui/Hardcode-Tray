#!/usr/bin/python3

from imp import load_source
from os import path
from sys import argv

filename = argv[3] + argv[4]
icon_to_repl = argv[2]
icon_for_repl = argv[1]
absolute_path = path.split(path.abspath(__file__))[0] + "/"
data_pack = load_source('data_pack', absolute_path + 'data_pack.py')
svgtopng = load_source('svgtopng', absolute_path + 'svgtopng.py')


filename_svg, file_extension = path.splitext(icon_for_repl)
if svgtopng.is_svg_enabled():
    if file_extension == '.svg':
        pngbytes = svgtopng.convert_svg2bin(icon_for_repl)
    else:
        with open(icon_for_repl, 'rb') as pngfile:
            pngbytes = pngfile.read()

    dataPack = data_pack.ReadDataPack(filename)
    dataPack.resources[int(icon_to_repl)] = pngbytes
    data_pack.WriteDataPack(dataPack.resources, filename, 0)
