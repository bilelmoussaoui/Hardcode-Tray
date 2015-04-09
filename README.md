# Hardcode-Tray
Fixes Hardcoded tray icons in Linux

#How to use
  1 - Install python3-cairosvg (used in case the original icons are .svg and the hardcoded icons are .png)
    ```bash
    sudo apt-get install python3-cairosvg 
  	```
  2 - Open the script.py using this command (root privileges needed because hardcoded icons are usually in `/opt`)
  ```bash
    sudo python3 script.py 
  ```
  3 - Enjoy!
  
### Supported applications
We now support : My-Weather-Indicator,Pushbullet-indicator, Touchpad-indicator,Variety, Grive-tools, Radiotray, yd-tools, Pomodoro-indicator

If you use an other applications and it's not supported yet? [Report an issue](https://github.com/bil-elmoussaoui/Hardcode-Tray/issues)
