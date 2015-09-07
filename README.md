# Hardcode-Tray
Fixes Hardcoded tray icons in Linux

The script will automagically detect your default theme, the right icon size, the hardcoded applications, the right icons for each indicator and fix them. All that with the possibilty to revert to the original icons.

For a better experience use [Numix icon theme](https://github.com/numixproject/numix-icon-theme).

### How to use
  1. Download the [zip folder](https://github.com/bil-elmoussaoui/Hardcode-Tray/archive/master.zip) or clone the repository
  ```bash
  git clone https://github.com/bil-elmoussaoui/Hardcode-Tray.git
  ```

  2. Install `python3-cairosvg`
  ```bash
  sudo apt-get install python3-cairosvg
  ```

  3. Install the patched version of `sni-qt` if you use any Qt applications or [build it](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-build-Sni-qt-from-source-code) from source code if you are using an other distro(Fedora, Arch)
  ```bash
  sudo add-apt-repository ppa:cybre/sni-qt-eplus
  sudo apt-get update && sudo apt-get dist-upgrade
  sudo apt-get install sni-qt

  ```
  4. Open the `script.py` using this command
  ```bash
  sudo -E python3 script.py
  ```

  5. Enjoy!


### Credits
- Modified version of `data_pack.py`, by The Chromium Authors released under a BSD-style license
- Chromuim icons, extracted from `chrome_100_percent.pak` released under BSD-style license
- Qt applications icons name by [elementaryPlus](https://github.com/mank319/elementaryPlus) team

### Hardcode-Tray wiki!
- [Changelog](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Changelog)
- [How does the script works?](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-does-the-script-works%3F)
- [How to contribute](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/How-to-contribute)
- [Supported applications](https://github.com/bil-elmoussaoui/Hardcode-Tray/wiki/Supported-applications)

You can fix [Viber](https://www.viber.com/) using [Viberwrapper-indicator](https://github.com/karas84/viberwrapper-indicator)
