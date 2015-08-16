# Hardcode-Tray
Fixes Hardcoded tray icons in Linux.

The script will automagically detect your default theme, the right icon size, the hardcoded applications, the right icons for each indicator and fix them. All that with the possibilty to revert to the original icons

For a better experience use [Numix icon theme](https://github.com/numixproject/numix-icon-theme)

### How to use
  1. Install python3-cairosvg (used in case the original icons are .svg and the hardcoded icons are .png)
  ```bash
    sudo apt-get install python3-cairosvg
  ```

  2. Install the patched version of ```sni-qt``` if you use any Qt applications
  ```bash
  sudo add-apt-repository ppa:cybre/sni-qt-eplus
  sudo apt-get update && sudo apt-get dist-upgrade
  sudo apt-get install sni-qt

  ```
  3. Open the script.py using this command (root privileges needed because hardcoded icons are usually in `/opt` or `/usr`)
  ```bash
    sudo -E python3 script.py
  ```
  using ``` sudo -E ``` instead of ``` sudo ``` to preserve environment variables  
  
  4. Enjoy!

### Credits
- Qt applications icons name by [elementaryPlus](https://github.com/mank319/elementaryPlus) team

### Supported applications
We now support:
* [Dropbox](https://www.dropbox.com/)
* [Flareget](http://flareget.com/)
* [Google Chrome](http://www.google.com/chrome/)
* [Google Music Manager](https://play.google.com/intl/ALL_fr/about/music/)
* [Grive-tools](https://launchpad.net/~thefanclub/+archive/ubuntu/grive-tools)
* [Keepassx](https://www.keepassx.org/)
* [Megasync](https://mega.co.nz/)
* [Mumble](https://launchpad.net/~mumble)
* [My-Weather-Indicator](https://launchpad.net/my-weather-indicator)
* [OwnCloud](https://owncloud.org/)
* [Pushbullet-indicator](https://launchpad.net/~atareao)
* [Radiotray](http://radiotray.sourceforge.net/)
* [Seafile](https://www.seafile.com/)
* [Skype](http://www.skype.com/)
* [Spotify](https://www.spotify.com)
* [Telegram](https://desktop.telegram.org/)
* [Tomahawk](https://www.tomahawk-player.org/)
* [Variety](http://peterlevi.com/variety/)
* [WizNote](http://www.wiznote.com/)
* [Yd-tools](https://github.com/slytomcat/yandex-disk-indicator)

We support a lot of applications, [More here..](https://github.com/bil-elmoussaoui/Hardcode-Tray/blob/master/db.csv)

You can fix [Viber](https://www.viber.com/) using [Viberwrapper-indicator](https://github.com/karas84/viberwrapper-indicator)

If you use an other applications and it's not supported yet? [Report an issue](https://github.com/bil-elmoussaoui/Hardcode-Tray/issues)
