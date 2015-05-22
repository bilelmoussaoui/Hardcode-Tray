# Hardcode-Tray
Fixes Hardcoded tray icons in Linux

###How to use
  1 - Install python3-cairosvg (used in case the original icons are .svg and the hardcoded icons are .png)
  
  ```bash
    sudo apt-get install python3-cairosvg 
  ```
  
  2 - Open the script.py using this command (root privileges needed because hardcoded icons are usually in `/opt`)
  ```bash
    sudo python3 script.py 
  ```
  
  3 - Choose the version you want to use (dark or light). Used for some apps like grive-tools
  
  4 - Enjoy!
  
### Supported applications
We now support : 

* [Grive-tools](https://launchpad.net/~thefanclub/+archive/ubuntu/grive-tools)
* [keepassx](https://www.keepassx.org/)
* [My-Weather-Indicator](https://launchpad.net/my-weather-indicator)
* [Pomodoro-indicator](https://github.com/malev/pomodoro-indicator)
* [Pushbullet-indicator](https://launchpad.net/~atareao)
* [Radiotray](http://radiotray.sourceforge.net/)
* [Touchpad-indicator](https://launchpad.net/touchpad-indicator)
* [Variety](http://peterlevi.com/variety/)
* [yd-tools](https://github.com/slytomcat/yandex-disk-indicator)

If you use an other applications and it's not supported yet? [Report an issue](https://github.com/bil-elmoussaoui/Hardcode-Tray/issues)
