from .utils import symlink_file, show_select_backup, create_backup_dir


def symlinks_installer(func):
    def wrapper(application, icon, icon_path):
        cname = application.__class__.__name__
        func(application, icon, icon_path)
        if "symlinks" in icon.keys():
            output_icon = icon_path +  icon["original"]
            for symlink_icon in icon["symlinks"]:
                if cname != "Application":
                  symlink_icon = '{0}.{1}'.format(
                                icon_path + symlink_icon,
                                icon["theme_ext"])
                else:
                    symlink_icon = icon_path + symlink_icon
                symlink_file(output_icon, symlink_icon)
    return wrapper


def install_wrapper(func):
    def wrapper(app):
        app.backup_dir = create_backup_dir(app.name)
        app.install_symlinks()
        func(app)
    return wrapper

def revert_wrapper(func):
    def wrapper(application):
        if application.BACKUP_IGNORE:
            application.remove_symlinks()
            func(application)
        else:
            application.selected_backup = show_select_backup(application.name)
            if application.selected_backup:
                application.remove_symlinks()
                func(application)
            else:
                application.is_done = False
    return wrapper
