# Smart-Mirror-Face-Recognition
Repositorio de los algoritmos usados para el proyecto:
https://github.com/pierreramiro/Smart-Mirror-Face-Recognition

## Detalles técnicos:
### Raspberry Pi 4B, 2GB ram
Este dispositivo se encargará del control de todos los periféricos establecidos en el proyecto y de la visualización de la interfaz gráfica del usuario.
### Motor NEMA 23 2.8A.
### DRIVER MOTOR TB6600
Este dispositivo tiene 3 pines de control: EN_pin, DIR_pin, PULL_pin. Con el pin EN_pin en baja, se puede habilitar el driver. El DIR_pin nos permitirá controlar el sentido de giro. Y el pin PULL_pin debe recibir pulsos según la configuración manual establecida en el driver con los switches. 
### Cámara web
### Sensor Ultrasonido HC-SR04
### Módulo Bluetooth HM-10
### Relés de estado sólido. Lógica Baja 3V3
### Luces RGB


## Funcionamiento del software:
Este proyecto se inicia en un modo Sleep, en donde se mueve la estructura del espejo hasta el tope y coloca las luces RGB en verde. En este estado se sondea la presencia de una persona y se verifica el rostro de la misma. Luego de haber identificado un rostro se entra al modo ActiveUser, en este modo se busca en la base de datos de la memoria si es un usuario conocido para poder configurar el espejo a los parámetros previamente establecidos, de no ser así, se coloca una configuración por defecto. En este estado se estará sondeando si se presiona el botón o si el usuario ha dejado de estar en el espejo. Sea el caso que el usuario se aleja, el espejo vuelve al estado modo Sleep. Pero, sea el caso que se presione el botón, se entra al modo BtConnected. En este estado se puede conectar por medio de una app movil en android para poder configurar al espejo. En esta aplicación existirán dos modos de usuario, el usuario básico y el usuario administrador. Como usuario básico solo se puede modificar la altura, mientras que como usuario administrador, se puede configurar los demás parámetros: altura del espejo, el color de las luces y la habilitación de las cargas de salida. Asimismo, el usuario administrador podrá tener la opción de agregar caras nuevas a la base de datos. En el caso que el usuario desee añadir nuevas caras se entra al modo AddingFace. En este modo se le solicita al usuario que defina el usuario a modificar/añadir el rostro y que, a su vez, se acerque a la cámara. Luego se vuelve al modo anterior, BtConnected. Finalmente, luego de realizar todas las configuraciones necesarias, el usuario se puede salir de este modo al desconectarse por medio del aplicativo y se vuelve al modo ActiveUser para repetir el proceso previamente explicado.

## Modos:
### Modo Sleep
Es el primer modo en el que entra el dispositivo y en el encendido realiza las configuraciones necesarias, como la carga de la base de datos de los rostros, la red entrenada para la detección de rostro, las configuraciones de los usuarios previamente establecida, las librería a usar, las declaración de funciones y variables a usar en el programa. Como configuración inicial y por defecto, se tiene que las luces son de color verde, la altura establecida es la máxima y las cargas están deshabilitadas.
En este modo, se sondea con el sensor de ultrasonido si se detecta algún tipo de presencia, en caso de detectar algo en el rango establecido, se configura las luces RGB en color blanco y se verifica con la cámara si existe algún rostro. De no ser así, simplemente se mantiene el color blanco hasta que el sensor deje de detectar presencia. En caso de detectar un rostro, se pasa al modo ActiveUser

### Modo ActiveUser
Según el rostro detectado se realiza un cálculo para identificar si se encuentra en la base de datos. En el caso que el rostro sea un rostro conocido, se establece la configuración de la misma, moviendo el espejo a la altura deseada, estableciendo el color de las luces RGB y las cargas adecuadas. Por otro lado, en el caso que no sea un rostro conocido se coloca una configuración por defecto: luces en blanco, solo carga 1 activa y la altura en el tope establecido.
Luego se sondea constantemente si se ha presionado el botón o si el sensor ultrasonido ya no detecta presencia. Para el caso que se presione el botón, se entra al modo BtConnected. Y para el caso en que no se detecte presencia, se verifica nuevamente con la cámara si no hay rostro detectable y vuelve al modo Sleep

### Modo BtConnected
Para realizar la conexión de Bluetooth se estableció la contraseña 0999.
En este modo se recibe por comunicación UART del módulo BT los datos que se reciben del aplicativo móvil. Según la data recibida se puede configurar solo las luces RGB como usuario básico, o se puede configurar todos los parámetros como usuario administrativo. En el caso de acceder como usuario administrativo, se tiene la posibilidad de acceder a la modificación del rostro, si se accede a esta opción se habilita el modo AddinngFace. 
Para salir de este modo y volver a ActiveUser se desconecta por medio del aplicativo.

### Modo AddingFace
En este modo se solicita al usuario acercar su rostro a la cámara para tomarle una cantidad definida de fotos. Luego el sistema se encarga de realizar el entrenamiento correspondiente del rostro.

## Clases:
### Ui_MainWindow
Esta clase contiene todos los widgets que componen la interfaz de usuario para el ActiveUser. Se definen el tamaño, el color de letra, el tamaño de fuente y las dimensiones de los botones, el color de fondo, entre otros.

### sleepModeDialog
Encargada de la configuración de la interfaz de usuario del modo SleepMode. Asimismo, contiene métodos para realizar el sondeo de presencia, rostro y el setup inicial.
### BT_DialogBoox
Encargada de la configuración de la interfaz de usuario del modo BtConnected. Asimismo contiene métodos para establecer la comunicación UART. 
### configureUser_DialogBox
Encargada de la configuración de la interfaz de usuario del modo AddingFace. Asimismo contiene métodos para realizar el entrenamiento y el guardado de los rostros.
### mirrolGUI
Esta clase se encarga de integrar las clases previamente mencionadas. Asimismo, se establecen temporizadores que serán usados de utilidad para actualizar la información de fecha, hora y temperatura. También, se establecen los métodos que realizan el control de los periféricos y su inicialización. Y se definen las variables globales que se usan en las demás clases. Cabe destacar que los métodos establecidos en esta clase son usados en las otras clases y contiene el control de los diálogos y las ventanas generadas para la interfaz del usuario

## Class mirrolGUI. Funciones:
### ConfigureGPIO

## Class sleepModeDialog. Funciones:
### ConfigureGPIO

## Class BT_DialogBoox. Funciones:
### ConfigureGPIO

## Class configureUser_DialogBox. Funciones:
### ConfigureGPIO

