cd /tmp
wget https://github.com/bil-elmoussaoui/Hardcode-Tray/archive/master.zip
unzip master.zip
cd ./Hardcode-Tray-master
rm -rf .git ./screenshots ./license
rm -f .gitignore README.md
cd ../
sudo mv Hardcode-Tray-master/ /opt/Hardcode-Tray
sudo ln -s /opt/Hardcode-Tray/hardcode-tray /usr/bin/hardcode-tray
