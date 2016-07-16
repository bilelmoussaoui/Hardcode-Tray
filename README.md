![Status](https://img.shields.io/badge/status-stable-green.svg) [![Hardcode-Tray release](https://img.shields.io/badge/release-v3.1-blue.svg)](https://github.com/bil-elmoussaoui/Hardcode-Tray/releases) ![Python version](https://img.shields.io/badge/python-3.4%2C%203.5-blue.svg)
# Hardcode-Tray

Fixes Hardcoded tray icons in Linux

The script will automagically detect your default theme, the right icon size, the hardcoded applications, the right icons for each indicator and fix them. All that with the possibilty to revert to the original icons.

For a better experience use [Numix icon theme](https://github.com/numixproject/numix-icon-theme).

### Screenshots
Before

![Before](screenshots/before.png)

After

![After](screenshots/after.png)


### How to use
  1. Install the script
  ```bash
  cd /tmp && wget -O - https://raw.githubusercontent.com/bil-elmoussaoui/Hardcode-Tray/master/install.sh | bash
  ```

  2. Install  `python3-cairosvg` or `inkscape`
    - Debian/Ubuntu : <br />
      `sudo apt-get install python3-cairosvg`<br />
      `sudo apt-get install inkscape`
    - Fedora : <br />
      `sudo dnf install python3-cairosvg`<br />
      `sudo dnf install inkscape`
    - Arch : <br />
      `sudo pacman -S python-cairosvg`<br />
      `sudo pacman -S inkscape`

  3. Install the patched version of `sni-qt`
    - Debian/Ubuntu :<br />
      <pre>
      sudo add-apt-repository ppa:cybre/sni-qt-eplus
      sudo apt-get update && sudo apt-get dist-upgrade
      sudo apt-get install sni-qt sni-qt:i386
      </pre>
    - Arch : <br />
      <pre>
      yaourt sni-qt-eplus
      yaourt lib32-sni-qt-eplus-bzr
      </pre>
  You can  [build it](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-build-Sni-qt) from source code if you are using an other distro (like Fedora).<br />
  The `sni-qt:i386` is used for 32 bits applications as Skype.<br />
  Teamviewer is also using the `sni-qt` package, however it is shipping its own version. Therefore this script also overwrites the version shipped by teamviewer with the patched one.
  4. Open Hardcode-Tray using this command<br/>
  <pre>hardcode-tray</pre>
  5. Enjoy!

### Options
- `--apply` and `--revert`

Hardcode-Tray shows by default a welcome message and ask the user to choose between applying the fix or reverting it. You can hide that using
```bash
hardcode-tray --apply
```
or

```bash
hardcode-tray --revert
```

- `--only`

You can use `--only` argument to fix/revert only one application, don't use the argument if you want to fix all applications your icon theme supports.
```bash
hardcode-tray --only telegram,skype
```

In order to get the names needed to fix only specific programs, you can look at the second column of [`db.csv`](https://github.com/bil-elmoussaoui/Hardcode-Tray/blob/master/db.csv). There you can find the corresponding name for the program you want to fix.

- `--path`

If you installed your app in a non standard location, you can override the path where the icons are stored using the `--path` argument. Only works in combination with the `--only` argument for a single application.
```bash
hardcode-tray --only telegram --path /home/user/telegram/
```

- `--size`

You can also use `--size 24/22/16` to force the script to use a different icon size or if the script does not detect your
desktop environment.
```bash
hardcode-tray --size 24 --only dropbox
```

- `--theme`

You can fix your hardcoded icons using an other theme than the default one.
```bash
hardcode-tray --theme Numix --only dropbox
```

- `--version`

You can print the version of Hardcode-Tray using
```bash
hardcode-tray --version
```

- `--update`

You can also update to the latest version of the script
```bash
hardcode-tray --update
```

### Uninstallation
To remove the script completely from your desktop you can use
```bash
cd /tmp && wget -O - https://raw.githubusercontent.com/bil-elmoussaoui/Hardcode-Tray/master/uninstall.sh | bash
```

### Credits
- Modified version of `data_pack.py`, by The Chromium Authors released under a BSD-style license
- Chromuim icons, extracted from `chrome_100_percent.pak` released under BSD-style license
- Qt applications icons name by [elementaryPlus](https://github.com/mank319/elementaryPlus) team

### Hardcode-Tray wiki!
- [Changelog](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Changelog)
- [FAQ](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/FAQ)
- [How to build the patched version of Sni-Qt](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-build-sni-qt)
- [How to contribute](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-contribute)
- [Supported applications](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Supported-applications)
