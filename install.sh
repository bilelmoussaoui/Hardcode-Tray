cd /tmp
echo "Downloading Hardcode-Tray ..."
version=$(git ls-remote -t https://github.com/bil-elmoussaoui/Hardcode-Tray.git | awk '{print $2}' | cut -d '/' -f 3 | cut -d '^' -f 1  | sort -b -t . -k 1,1nr -k 2,2nr -k 3,3r -k 4,4r -k 5,5r | uniq)
wget -q https://github.com/bil-elmoussaoui/Hardcode-Tray/archive/$version.zip
unzip -oq $version.zip
rm -f $version.zip
versionnb=$(version | sed "s/[^0-9. ]*//g")
cd ./Hardcode-Tray-$versionnb
rm -rf .git ./screenshots ./license
rm -f .gitignore README.md install.sh uninstall.sh
cd ../
if [ -d "/opt/Hardcode-Tray" ];then
    sudo rm -rf /opt/Hardcode-Tray
fi
sudo mv Hardcode-Tray-$versionnb/ /opt/Hardcode-Tray
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
