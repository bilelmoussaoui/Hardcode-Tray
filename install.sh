cd /tmp
echo "Downloading Hardcode-Tray ..."
wget -q https://github.com/bil-elmoussaoui/Hardcode-Tray/archive/master.zip
unzip -oq master.zip
rm -f master.zip
cd ./Hardcode-Tray-master
rm -rf .git ./screenshots ./license
rm -f .gitignore README.md install.sh uninstall.sh
cd ../
if [ -d "/opt/Hardcode-Tray" ];then
    sudo rm -rf /opt/Hardcode-Tray
fi
sudo mv Hardcode-Tray-master/ /opt/Hardcode-Tray
echo "Creating symbolic link.."
if [ -L "/usr/bin/hardcode-tray" ];then
    sudo rm -f /usr/bin/hardcode-tray
fi
sudo ln -s /opt/Hardcode-Tray/hardcode-tray /usr/bin/hardcode-tray
if [ "$1" == "--u" ]; then
    echo "The update has completed successfully."
else
    echo "Installation completed successfully."
fi
echo "You can run the script using 'hardcode-tray'"
