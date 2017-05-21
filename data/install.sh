#!/bin/bash
cd /tmp || exit
if [ -d "/tmp/Hardcode-Tray/" ]; then
    sudo rm -rf /tmp/Hardcode-Tray
fi
echo "Downloading Hardcode-Tray ..."
if [ "$1" == "--g" ]; then
    echo "Cloning the repository..."
    if [ -d "./Hardcode-Tray" ]; then
    	rm -rf /tmp/Hardcode-Tray
    fi
    git clone https://github.com/bil-elmoussaoui/Hardcode-Tray
    cd ./Hardcode-Tray
else
    echo "Downloading the latest version..."
    version=$(git ls-remote -t https://github.com/bil-elmoussaoui/Hardcode-Tray.git | awk '{print $2}' | cut -d '/' -f 3 | cut -d '^' -f 1  | sort -b -t . -k 1,1nr -k 2,2nr -k 3,3r -k 4,4r -k 5,5r | uniq)
    IFS=' ' read -r -a versions <<< "$version"
    version=${versions[0]}
    wget -q https://github.com/bil-elmoussaoui/Hardcode-Tray/archive/"$version".zip
    unzip -oq "$version".zip
    rm -f "$version".zip
    versionnb=${version//[a-zA-Z]/}
    cd ./Hardcode-Tray-"$versionnb" || exit
fi
rm -rf .git ./screenshots
rm -f .gitignore README.md data/install.sh data/uninstall.sh
cd ../ || exit
if [ -d "/opt/Hardcode-Tray" ]; then
    sudo rm -rf /opt/Hardcode-Tray
fi
if [ "$1" == "--g" ]; then
    sudo mv Hardcode-Tray/ /opt/Hardcode-Tray
else
    sudo mv Hardcode-Tray-"$versionnb"/ /opt/Hardcode-Tray
fi
echo "Creating symbolic link.."
if [ -L "/usr/bin/hardcode-tray" ] || [ -f "/usr/bin/hardcode-tray" ];
then
    sudo rm -f /usr/bin/hardcode-tray
fi
sudo ln -s /opt/Hardcode-Tray/hardcode-tray /usr/bin/hardcode-tray
if [ "$1" == "--u" ]; then
    echo "The update has completed successfully."
elif [ "$1" == "--g" ]; then
    echo "Hardcode-Tray was updated to git version successfully."
else
    echo "Installation completed successfully."
fi
echo "You can run the script using 'hardcode-tray'"
