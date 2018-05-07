#!/bin/bash

# Install git for pulling the code from the repository
echo "Verifying/Installing git"
wait
sudo apt-get install -y git
status=$?
wait
if [ $status -ne 0 ]; then
    echo "unable to access git...aborting"
    echo "contact dave@KiloWattsforHumanity.org for assistance"
fi

# Move to root and download data logger code from github
cd /
echo ""
echo "Downloading data logger software to the root directory in /KWH"
wait
sudo git clone https://github.com/sbcdave/KWH.git
status=$?
wait
if [ $status -ne 0 ]; then
    echo ""
    echo "GitHub download stalled...rerun DASInstaller.sh"
    echo ""
    exit
fi

# Change data logger code root directory owner:group to pi
echo ""
echo "Updating /KWH permissions"
wait
sudo chown -R pi:pi KWH
wait

#investigate shutting down uneccesary services

# Create symlink from /etc/defaults to datalogger.conf file
echo ""
echo "Ensuring datalogger config is used at boot and setting auto-login to console"
wait
sudo ln -n /KWH/datalogger/config/datalogger.conf /etc/default/datalogger.conf
wait
# Add datalogger.conf file to root and pi's .bashrc
sudo cp /KWH/moves/.bashrc /root/.bashrc
wait
cp /KWH/moves/.bashrc /home/pi/.bashrc
wait
# Source the aliases functions and environment variables
. ~/.bashrc
wait
sudo cp /KWH/moves/autologin@.service /etc/systemd/system/autologin@.service
wait
sudo systemctl daemon-reload
wait
sudo systemctl enable autologin@.service
wait

# Setting up SIM communications on ttyAMA0
echo ""
echo "Enabling ttyAMA0 on TX/RX for SIM comms"
wait
sudo systemctl mask serial-getty@ttyAMA0.service
wait

# Adjusting /boot/config.txt for SIM and Temp sensors communications
echo ""
echo "Updating /boot/config.txt to enable SIM and Temp sensor comms"
wait
sudo cp /KWH/moves/config.txt /boot/config.txt
wait

# Enable simserver.service
echo ""
echo "Enabling sim server service"
sudo cp /KWH/moves/simserver.service /etc/systemd/system/.
wait
sudo systemctl enable simserver.service
wait
sudo systemctl start simserver.service
wait

# Switching keyboard layout to US
echo ""
echo "Switching keyboard layout to US"
sudo cp /KWH/moves/keyboard /etc/default/keyboard

# Activate 1 minute transmission via cron
echo ""
echo "Enabling cron jobs"
wait
sudo cp /KWH/moves/dcrond /etc/cron.d/dcrond
wait
sudo chmod 644 /etc/cron.d/dcrond
wait

# Reboot to finalize
echo ""
echo "Installation complete. Reboot to enable communications with PCB."
echo "Reboot now(y/n)?"
read ans
if [ "$ans" = "y" ]; then
    echo "Thank you, and enjoy...courtesy of KiloWatts for Humanity"
    sudo shutdown -r now
else
    echo "Several error logs will fill with communications issues until reboot"
    echo "Thank you, and enjoy...courtesy of KiloWatts for Humanity"
fi

