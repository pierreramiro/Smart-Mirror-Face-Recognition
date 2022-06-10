rfkill unblock all
sudo service bluetooth restart
sleep 2
sudo /etc/init.d/bluetooth stop
sudo /etc/init.d/bluetooth start #enciende el bluetooth
sudo hciconfig hci0 piscan #makes discoverable
sudo systemctl enable bluetooth-autoconnect.service
sudo systemctl start bluetooth-autoconnect.service
#Habilitamos
echo "agent off" | bluetoothctl
#echo "power off" | bluetoothctl
echo "power on" | bluetoothctl
echo "agent NoInputNoOutput" | bluetoothctl
echo "scan on" | bluetoothctl
echo "discoverable on" | bluetoothctl
echo "pairable on" | bluetoothctl
echo "agent on" | bluetoothctl
echo "default-agent" | bluetoothctl
sleep 2
python3 ~/Documents/Github/Smart-Mirror-Face-Recognition/Bluetooth/EI_Bluetooth.py

# #Scan y guardamos los dispositivos en un file
# hcitool -i hci0 scan > text.txt
# #Mostramos en pantalla
# input="text.txt"
# while IFS= read -r line
# do
#     echo "$line"
# done < "$input"
# #
# echo "Cual es tu dispositivo?"
# read opt
# #Limpiamos data y obtenemos el string del MAC addr deseado

# #Damos un tiempo
# #Eliminamos dispositivo
# echo "remove D4:38:9C:CB:5D:3A" | bluetoothctl
# #Confiamos en el dispositivo
# echo "trust D4:38:9C:CB:5D:3A" | bluetoothctl
# #Hacemos la conexion
# echo "connect D4:38:9C:CB:5D:3A" | bluetoothctl
# #python3 server2.py



