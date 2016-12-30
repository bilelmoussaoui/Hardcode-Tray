[![Code Issues](https://www.quantifiedcode.com/api/v1/project/6ebdcd35681d424285ddf9e00e74b6e2/badge.svg)](https://www.quantifiedcode.com/app/project/6ebdcd35681d424285ddf9e00e74b6e2)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4d5c0768b874407bb1dcc2f928899ba5)](https://www.codacy.com/app/bil-elmoussaoui/Hardcode-Tray?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bil-elmoussaoui/Hardcode-Tray&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/4d5c0768b874407bb1dcc2f928899ba5)](https://www.codacy.com/app/bil-elmoussaoui/Hardcode-Tray?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bil-elmoussaoui/Hardcode-Tray&amp;utm_campaign=Badge_Coverage)
[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/Hardcode-Tray/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link)
[![Hardcode-Tray
release](https://img.shields.io/badge/release-v3.6.2-blue.svg)](https://github.com/bil-elmoussaoui/Hardcode-Tray/releases)

# Hardcode-Tray

Fixes Hardcoded tray icons in Linux

The script will automatically detect your default theme, the right icon size, the hard-coded applications, the right icons for each indicator and fix them. All that with the possibility to revert to the original icons.

### Themes
Here's a list of themes that supports Hardcode-Tray:
  - [Numix icon theme](https://github.com/numixproject/numix-icon-theme)

 <div align="center"><img src="screenshots/numix.png" alt="Preview" /></div>

  - [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)

 <div align="center"><img src="screenshots/papirus.png" alt="Preview" /></div>

### Install

#### Arch Linux (AUR):
Stable version:
```bash
yaourt -S hardcode-tray
```
Developpement version:
```bash
yaourt -S hardcode-tray-git
```
#### Ubuntu 14.04 / 16.04 / 16.10 / 17.04 (PPA):
```bash
sudo add-apt-repository ppa:andreas-angerer89/sni-qt-patched
sudo apt update
sudo apt install sni-qt sni-qt:i386 hardcode-tray
```
#### Manual install
  1. Download and install the script:
  ```bash
  cd /tmp && wget -O - https://raw.githubusercontent.com/bil-elmoussaoui/Hardcode-Tray/master/install.sh | bash
  ```

  2. Install dependencies:
   - `git`
   - `wget`
   - `python3`
   - `python3-gi`
   - [`patched sni-qt`](https://launchpad.net/~cybre/+archive/ubuntu/sni-qt-eplus) <br>
   2.1. Pick your favorite conversion tool
     1. - `python3-cairosvg`
     2. - `librsvg`
     3. - `inkscape`

  You can build [the patched version of sni-qt](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-build-Sni-qt) from source code if you are using another distro (like Fedora).<br />
  The `sni-qt:i386` is used for 32 bits applications as Skype.<br />
  Teamviewer is also using the `sni-qt` package. However, it is shipping its own version. Therefore this script also overwrites the version shipped by TeamViewer with the patched one.
  4. Open Hardcode-Tray using this command<br/>
  <pre>hardcode-tray</pre>
  5. Enjoy!

### Options
- `--apply` and `--revert`

Hardcode-Tray shows by default a welcome message and asks the user to choose between applying the fix or reverting it. You can hide that using
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
hardcode-tray --only telegram, skype
```

In order to get the names needed to fix only specific programs, you can look at the `app_name` key in the JSON files for the program. There you can find the corresponding name for the program you want to fix.

- `--path`

If you installed your app in a non-standard location, you can override the path where the icons are stored using the `--path` argument. Only works in combination with the `--only` argument for a single application.
```bash
hardcode-tray --only telegram --path /home/user/telegram/
```

- `--size`

You can also use `--size {24,22,16}` to force the script to use a different icon size or if the script does not detect your desktop environment.
```bash
hardcode-tray --size 24 --only dropbox
```

- `--theme`

You can fix your hardcoded icons using another theme than the default one.
```bash
hardcode-tray --theme Numix --only dropbox
```

- `--light-theme` and `--dark-theme`

Some applications provide dark and light tray icons with the possibility to modify them using their UI. In order to use a dark theme for dark icons and a light one for light icons, you can use those two arguments. It only works if you use both of them at the same time.
```bash
hardcode-tray --dark-theme Numix-light --light-theme Numix
```

- `--conversion-tool`

Hardcode-Tray by default detects if the user has either Inkscape, RSVGConvert or Cairo installed and use one of them to convert SVG icons to PNG. In order to choose the tool to use you if one of them is broken in your installation.
```bash
hardcode-tray --conversion-tool {Inkscape,Cairo, RSVGConvert}
```
For now, we only support Inkscape and Cairo(CairoSVG)

Cairo has some issues with converting SVG files that use CSS (see [#245](https://github.com/bil-elmoussaoui/Hardcode-Tray/issues/245)).

- `--change-color`

Your favorite theme does not provide icons for all those hardcoded icons? Just use an other theme and change the colors using Hardcode-Tray.
```bash
hardcode-tray --change-color "#FIRSTCOLOR #REPLACE_FIRST_COLOR" "#SECONDCOLOR #REPLACE_SECOND_COLOR"...
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

- `--update-git`

You can also update to the git version of the script
```bash
hardcode-tray --update-git
```

### Uninstallation
To remove the script completely from your desktop you can use
```bash
cd /tmp && wget -O - https://raw.githubusercontent.com/bil-elmoussaoui/Hardcode-Tray/master/uninstall.sh | bash
```

### Credits
- Modified version of `data_pack.py`, by The Chromium Authors released under a BSD-style license
- Qt applications icons name by [elementaryPlus](https://github.com/mank319/elementaryPlus) team

### Hardcode-Tray wiki!
- [Changelog](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Changelog)
- [FAQ](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/FAQ)
- [How to build the patched version of Sni-Qt](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-build-sni-qt)
- [How to contribute](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-contribute)
- [Supported applications](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Supported-applications)
