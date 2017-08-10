

from re import findall, match, sub
from os import path

def get_iterated_icons(icons):
    """Used to avoid multiple icons names, like for telegram."""
    new_icons = []
    for icon in icons:
        search = findall(r"{\d+\-\d+}", icon)
        if len(search) == 1:
            values = search[0].strip("{").strip("}").split("-")
            minimum, maximum = int(values[0]), int(values[1])
            for i in range(minimum, maximum + 1):
                new_icons.append(icon.replace(search[0], str(i)))
        else:
            new_icons.append(icon)
    return new_icons


def get_pngbytes(icon):
    """Return the pngbytes of a svg/png icon."""
    from HardcodeTray.app import App
    icon_for_replace = icon.theme
    icon_extension = icon.theme_ext
    icon_size = icon.icon_size
    if icon_extension == 'svg':
        if icon_size != App.icon_size():
            png_bytes = App.svg().to_bin(icon_for_replace,
                                         App.icon_size())
        else:
            png_bytes = App.svg().to_bin(icon_for_replace)
    elif icon_extension == "png":
        with open(icon_for_replace, 'rb') as png_file:
            png_bytes = png_file.read()
    else:
        png_bytes = None
    return png_bytes


# Functions used in the electron script

def replace_to_6hex(color):
    """Validate and replace 3hex colors to 6hex ones."""
    valid_color_regex = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
    if match(valid_color_regex, color):
        if len(color) == 4:
            color = "#{0}{0}{1}{1}{2}{2}".format(color[1], color[2], color[3])
        return color.upper()
    return None


def replace_colors(file_name, colors):
    """Replace the colors in a file name."""
    if path.isfile(file_name):
        # Open SVG file
        with open(file_name, 'r') as file_:
            file_data = file_.read()

        # Replace colors
        for color in colors:
            to_replace = color[0]
            for_replace = color[1]
            file_data = sub(to_replace, for_replace, file_data)

        # Save new file content on a tmp file.
        with open(file_name, 'w') as _file:
            _file.write(file_data)
