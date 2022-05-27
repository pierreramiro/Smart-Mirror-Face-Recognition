sudo /etc/init.d/bluetooth start #enciende el bluetooth
#sudo /etc/init.d/bluetooth stop #apaga el bluetooth
sudo hciconfig hci0 piscan #Enable inquiry scan and page scan of RPi's Bluetooth Server
#sudo hciconfig -a hci0 | grep -i 'PSCAN *ISCAN' #Chequeamos si en realidad se hizo discoverable

