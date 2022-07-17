## How to excute app on boot
Los archivos y directorios que se utilizan en la ejecución de la GUI son los siguientes:
- dataset  (dir)
- resources (dir)
- encodings.pickle (file)
- haarcascade_frontalface_default.xml (file)
- main.py
- MainWindow.py (file)
- mirrollGUI.py (file)
- userConfig.scv (file)

Asimismo, se debe asegurar que el archivo main.py tenga el su 1era línea los siguiente:
```
#!/usr/bin/env python
```

Estos archivos deben colocarse en "/home/NAME_OS" o en su defecto "~"

Luego se procede a crear un autorun-file. Esto lo hacemos con los siguientes pasos. (referencia: https://stackoverflow.com/questions/50367837/pyqt-how-to-run-gui-on-raspberry-pi-desktop-startup)

```
cd /home/pi/.config/autostart #Si la carpeta no existe, la creamos.
sudo nano mirrollBoot.desktop
```

En el archivo colocamos lo siguiente:

```
[Desktop Entry]
Encoding=UTF-8
Name=my
Comment=comentario
Icon=gnome-info
Exec=python3 /home/NAME_OS/main.py
Terminal=false
Type=Application

X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=0
```

Se guarda el archivo y se reinicia el sistema para corroborar la configuración. Asimismo, se recomienda colocar un fondo de pantalla oscuro o con el icono de Mirroll "dormido"
