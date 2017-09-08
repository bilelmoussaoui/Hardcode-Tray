from re import match
from gi.repository import Gio

from HardcodeTray.log import Logger
from HardcodeTray.const import KDE_CONFIG_FILE


def kde_scaling_factor():
    """Return the widgets scaling factor on KDE."""
    scaling_factor = None
    was_found = False

    try:
        with open(KDE_CONFIG_FILE, 'r') as kde_obj:
            data = kde_obj.readlines()

        for line in data:
            line = list(map(lambda x: x.strip(),
                            line.split("=")))

            if len(line) == 1:
                was_found = match(
                    r'\[Containments\]\[[0-9]+\]\[General\]', line[0])

            if len(line) > 1 and was_found and line[0].lower() == "iconsize":
                scaling_factor = int(line[1])
                break
        if scaling_factor:
            Logger.debug("Scaling Factor/KDE: {}".format(scaling_factor))

        return scaling_factor
    except (FileNotFoundError, KeyError) as kde_error:
        Logger.debug("Scaling Factor/KDE not detected.")
        Logger.error(kde_error)
    return None


def gnome_scaling_factor():
    """Return gnome scaling factor."""
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.gnome.desktop.interface", True):
        gsettings = Gio.Settings.new("org.gnome.desktop.interface")
        scaling_factor = gsettings.get_uint('scaling-factor') + 1
        Logger.debug("Scaling Factor/GNOME: {}".format(scaling_factor))
        return scaling_factor
    else:
        Logger.debug("Scaling Factor/Gnome not detected.")
    return 1


def cinnamon_scaling_factor():
    """Return Cinnamon desktop scaling factor."""
    source = Gio.SettingsSchemaSource.get_default()
    if source.lookup("org.cinnamon.desktop.interface", True):
        gsettings = Gio.Settings.new("org.cinnamon.desktop.interface")
        scaling_factor = gsettings.get_uint('scaling-factor')
        if scaling_factor == 0:
            # Cinnamon does have an auto scaling feature which we can't use
            scaling_factor = 1
        Logger.debug("Scaling Factor/Cinnamon: {}".format(scaling_factor))
        return scaling_factor
    else:
        Logger.debug("Scaling Factor/Cinnamon not detected")
    return 1
