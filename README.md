# Hardcode-Tray
Fixes Hardcoded tray icons in Linux

### How to use
  1. Install python3-cairosvg (used in case the original icons are .svg and the hardcoded icons are .png)
  ```bash
    sudo apt-get install python3-cairosvg
  ```
  
  2. Install inkscape, if you don't use Spotify ignore this step (used to convert .svg icons to .ico)
  ```bash
  sudo apt-get install inkscape
  ```
  3. Install the patched version of ```sni-qt``` if you use any qt applications
  ```bash
  sudo add-apt-repository ppa:bkanuka/sni-qt
  sudo apt-get update && sudo apt-get dist-upgrade
  sudo apt-get install sni-qt

  ```  

  4. Open the script.py using this command (root privileges needed because hardcoded icons are usually in `/opt` or `/usr`)
  ```bash
    sudo python3 script.py
  ```
  
  5. Enjoy!

### Supported applications
We now support:
* [Calendar-indicator](https://bugs.launchpad.net/calendar-indicator)
* [Catch-indicator](https://launchpad.net/~atareao)
* [Cryptfolder-indicator](https://launchpad.net/~atareao)
* [Dropbox](https://www.dropbox.com/)
* [Google-tasks-indicator](https://launchpad.net/~atareao)
* [Grive-tools](https://launchpad.net/~thefanclub/+archive/ubuntu/grive-tools)
* [Keepassx](https://www.keepassx.org/)
* [My-Weather-Indicator](https://launchpad.net/my-weather-indicator)
* [OwnCloud](https://owncloud.org/)
* [Pomodoro-indicator](https://github.com/malev/pomodoro-indicator)
* [Pushbullet-indicator](https://launchpad.net/~atareao)
* [Prime-indicator](https://github.com/beidl/prime-indicator)
* [Radiotray](http://radiotray.sourceforge.net/)
* [Spotify](https://www.spotify.com)
* [Telegram](https://desktop.telegram.org/)
* [Touchpad-indicator](https://launchpad.net/touchpad-indicator)
* [Twitch-indicator](https://github.com/rbrs/twitch-indicator)
* [Variety](http://peterlevi.com/variety/)
* [Xkbmod-indicator](https://github.com/sneetsher/indicator-xkbmod)
* [Yd-tools](https://github.com/slytomcat/yandex-disk-indicator)
* [Youtube-indicator](https://github.com/slytomcat/yandex-disk-indicator)

You can fix [Viber](https://www.viber.com/) using [Viberwrapper-indicator](https://github.com/karas84/viberwrapper-indicator)

If you use an other applications and it's not supported yet? [Report an issue](https://github.com/bil-elmoussaoui/Hardcode-Tray/issues)
