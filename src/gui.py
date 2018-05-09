from appJar import gui
from PIL import Image, ImageTk

import tkinter
import os
import threading
import time
import signal
import sys
import socket

# nuestros ficheros
import servidorDescubrimiento as SD
import comunicacionTCP as TCP

class Gui:
	"""
    CLASE: Gui
    DESCRIPCION: 
    	Es la interfaza grafica de la aplicacion.
		Todo lo relacionado con ella y sus cambios se tratan en este modulo.
    """

	# Files, definidas asi por defecto. 
	authenticationFile = "authentication.dat"
	logo = "logo.gif"
	videoBoxImage = "callicon.gif"
	webCamBoxImage = "dandelions.gif"

	videoDir = "/media"
	
	# Configuracion de colores de la aplicacion. En busqueda de la mejor combinacion...
	bgColor = "OrangeRed"
	listColor = "LightGrey"

	# Objetos de clase necesarios (inicializados en constructor).
	server = None
	tvideo = None
	comtcp = None

	# Util para Widget
	userList = []
	videoList = []

	# Thread que escucha comandos
	listeningThread = None

	# Flag para distinguir si estamos en llamada o no
	inCall = False

	# Credenciales del usuario que inicia sesion
	username = None
	pwd = None


	def __init__(self):
		"""
		FUNCION: Constructor del modulo interfaz grafica
		ARGS_IN: 
				-
		DESCRIPCION:
				Construye el objeto principal de la aplicacion.
		ARGS_OUT:
				-
		"""
		self.app = gui("Login Window", "1000x600")
		self.app.setTitle("Cyder VideoChat")
		self.app.setIcon(self.logo)
		self.app.setBg(self.bgColor)
		self.app.setResizable(canResize=False)

		self.username = None
		self.pwd = None

		d = {}
		try:
			with open("client.conf", "r") as f:
				for line in f:
				    (key, val) = line.split()
				    print(line)
				    d[key] = val


			self.portSD = d['portSD']
			self.portTCP = d['portTCP']
			print(self.portTCP)
			self.publicIPEnabled = d['publicIPEnabled']
			self.portUDP = d['portUDP']

			# Si el flag de IP publica esta activado, se toma IP del fichero de configuracion
			if self.publicIPEnabled == 'Y':
				self.IPAddress = d['IP']

			else:
			# Si no esta activo, asumimos que existe una conexion a Internet y cogemos nuestra IP Local
				testSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				testSock.connect(("vega.ii.uam.es", 8000))
				self.IPAddress = testSock.getsockname()[0]
				testSock.close()

		except (EnvironmentError, Exception):

			print ("ERROR: El fichero de configuracion no tiene el formato adecuado")
			return 

				
		self.server = SD.servidorDescubrimiento(portSD= self.portSD)

		self.comtcp = TCP.ComunicacionTCP(gui= self, myIP= self.IPAddress, listenPort= self.portTCP, serverPort= self.portSD, myUDPport= self.portUDP)

		self.app.setStopFunction(self.checkStop)
		
		signal.signal(signal.SIGINT, self.signal_handler)


	def signal_handler(self, signal, any):
		"""
		FUNCION: signal_handler(self, signal, any)
		ARGS_IN: 
				* signal: Senial a manejar aqui
				* any: Argumento necesario para que funcione signal		
		DESCRIPCION:
				Realiza un cierre seguro si se utiliza Ctrl+C o el boton X en el limite superior derecho.
		ARGS_OUT:
				-
		"""

		if self.inCall == True:
				self.colgar()
		sys.exit(0)
	
	def checkStop(self):
		"""
		FUNCION: checkStop(self)
		ARGS_IN: 
		DESCRIPCION:
				Funcion que se ejecuta al pulsar el boton X en el limite superior derecho antes de hacer Crtl C.
				En nuestro caso, como tenemos un manejador propio de Ctrl C devuelve siempre True.
		ARGS_OUT:
				-
		"""

		return True


	def startGUI(self):
		"""
		FUNCION: startGUI(self)
		ARGS_IN: 
		DESCRIPCION:
			Realiza un intento de login automatico, si no lo consigue, muestra la pantalla de login normal.
		ARGS_OUT:
				-
		"""

		try:
			self.loginFromFile()
		except (EnvironmentError, ValueError):
			self.setLoginLayout()
			self.app.go()

	def loginFromFile(self): 
		"""
		FUNCION: loginFromFile(self)
		ARGS_IN: 
		DESCRIPCION:
			Itenta realizar un login automatico a partir del archivo authentication.dat.
		ARGS_OUT:
				-
		"""
		try:
			d = {}
			with open("authentication.dat", "r") as f:
				# Guardamos todos los valores que haya en el fichero
				for line in f:
				    (key, val) = line.split()
				    d[key] = val

			username = d['username']
			pwd = d['pwd']

		except (EnvironmentError, ValueError, KeyError):
			raise EnvironmentError("No authentication file")
			return
			
		state = self.server.confirmarUsername(self.portTCP, self.IPAddress, username, pwd)
		if state == "OK":

			self.username = username
			self.pwd = pwd
			self.setUsersLayout()
			self.endEvent = threading.Event()		
			self.listeningThread = threading.Thread(target= self.comtcp.listening, args=(self.endEvent,))
			self.listeningThread.setDaemon(True)
			self.listeningThread.start()
			self.app.go()
		else: 
			os.remove(self.authenticationFile)
			self.setLoginLayout()

	def login(self):
		"""
		FUNCION: login(self)
		ARGS_IN: 
		DESCRIPCION:
			Extrae los credenciales de los campos correspondientes y se comunica con el servidor para verificar 
			la identidad del usuario. Si todo va bien, muestra la pantalla principal de la aplicacion.
		ARGS_OUT:
				-
		"""
		username = self.app.getEntry("Usuario:   ")
		pwd = self.app.getEntry("Contraseña:   ")

		if username.count('#') != 0 :
			self.app.errorBox("Error en login", "Su usuario no puede contener '#' ni otros caracetres extraños")
			self.app.setEntry("Usuario:   ", "", callFunction=False)
			self.app.setEntry("Contraseña:   ", "", callFunction=False)
			return 

		# arreglar 3er argumento
		state = self.server.solicitarUsername(self.portTCP, self.IPAddress, username , pwd)
		if state == "OK":
			self.username = username
			self.pwd = pwd
			self.setUsersLayout()
		else:
			self.app.errorBox("Error en login", "Intentelo de nuevo")

	def logout(self):
		"""
		FUNCION: logout(self)
		ARGS_IN: 
		DESCRIPCION:
			Sale de la sesion y muestra otra vez la pantalla del login
		ARGS_OUT:
				-
		"""
		self.username = None
		self.pwd = None
		os.remove(self.authenticationFile)
		
		if self.inCall == True:
			self.colgar()

		self.setLoginLayout()

		
	def loginButtons(self, btnName):
		"""
		FUNCION: loginButtons(self, btnName)
		ARGS_IN:
			* btnName: Nombre del boton que se ha pulsado. 
		DESCRIPCION:
			Funcion para parsear los eventos de los botones de la pantalla del login
		ARGS_OUT:
				-
		"""
		if btnName == "Exit":
		    self.app.stop()
		if btnName == "Login":
		    self.login()
		  
	def actualizarUsuarios(self):
		"""
		FUNCION: actualizarUsuarios(self)
		ARGS_IN: 
		DESCRIPCION:
			Funcion que actualiza la lista de usuarios del panel principal- 
			Para ello, se comunica con el servidor.
		ARGS_OUT:
				-
		"""
		self.userList = self.server.listarUsuarios()

		self.app.clearListBox("userList", callFunction=True)

		# nos eliminamos de la lista de usuarios a nosotros mismos para evitar problemas
		if self.username != None and self.username != "":
			self.userList.remove(self.username)

		for item in self.userList:
			if item != "":
				self.app.addListItem("userList", item)
				self.app.setListItemBg("userList", item, self.listColor)


	def buscar(self):
		"""
		FUNCION: buscar(self)
		ARGS_IN: 
		DESCRIPCION:
			Busca de entre la lista de usuarios las coincidencias con lo que esta escrito en el campo Busqueda
		ARGS_OUT:
				-
		"""


		Busqueda_term = self.app.getEntry("Busqueda: ")
		
		self.app.clearListBox("userList", callFunction=True)



		for item in self.userList:
			if Busqueda_term.lower() in item.lower():
				self.app.addListItem("userList", item)
				self.app.setListItemBg("userList", item, self.listColor)

	

	def cambiarFrameVideo(self, frame):
		"""
		FUNCION: cambiarFrameVideo(self, frame)
		ARGS_IN: 
				* frame: Frame que va a sustiuir al anterior.
		DESCRIPCION:
			Cambia el frame de video principal por el "frame" pasado como argumento. Es decir, el del medio.
		ARGS_OUT:
				-
		"""
		self.app.setImageData("videoBox", frame, fmt = 'PhotoImage')

	def cambiarFrameWebCam(self, frame):
		"""
		FUNCION: cambiarFrameWebCam(self, frame)
		ARGS_IN: 
				* frame: Frame que va a sustiuir al anterior.
		DESCRIPCION:
			Cambia el frame de nuestro propio video por el "frame" pasado como argumento. Es decir, el del la derecha.
		ARGS_OUT:
				-
		"""
		self.app.setImageData("webCamBox", frame, fmt = 'PhotoImage')


	def llamar(self):
		"""
		FUNCION: llamar(self)
		ARGS_IN: 
		DESCRIPCION:
			Realiza una llamada al usuario seleccionado de la lista de Usuarios.
			Si no hay ninguno, emerge un PopUp avisando.
			Si ya estas en una llamada, lo mismo.
			Si por lo que fuera no pudieramos establecer comunicacion con un usuario, tambien nos avisa.
		ARGS_OUT:
				-
		"""
		users = self.app.getListBox("userList")
		print("Estas haciendo una llamada1")
		if users:
			user = users[0]
			if user != None:
				infoUser = self.server.getInfoUsuario(user)
				ip = infoUser['ip']
				print("Estas haciendo una llamada2")
				if self.inCall == True:
					ret = self.app.okBox("ERROR", "Para llamar a otro usuario necesitas colgar la videollamada actual", parent=None)

					if ret == False:
						return
					elif ret == True:
						self.colgar()
				
				if ip == None:
					self.app.errorBox("ERROR", "Hay un problema con el usuario: {} .\n No se puede realizar la llamada".format(user))
					return 

				self.comtcp.send_calling(ipDest= ip, portDest= infoUser['listenPort'] , username= self.username)

			else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")
		else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")

	
	def colgar(self):
		"""
		FUNCION: colgar(self)
		ARGS_IN: 
		DESCRIPCION:
			Si el usuario esta en una llamada, cuelga.
		ARGS_OUT:
				-
		"""
		
		if self.inCall == True:
			self.comtcp.send_end(self.comtcp.peerIP, self.comtcp.peerCommandPort, self.username)
 
	def play(self):
		"""
		FUNCION: play(self)
		ARGS_IN: 
		DESCRIPCION:
			Si el usuario esta en una llamada pausada, la reanuda.
		ARGS_OUT:
				-
		"""
		
		if self.inCall == True:
			self.comtcp.send_resume(self.comtcp.peerIP, self.comtcp.peerCommandPort, self.username)

	def pause(self):
		"""
		FUNCION: pause(self)
		ARGS_IN: 
		DESCRIPCION:
			Si el usuario esta en una llamada,  la pausa.
		ARGS_OUT:
				-
		"""
		
		if self.inCall == True:
			self.comtcp.send_hold(self.comtcp.peerIP, self.comtcp.peerCommandPort, self.username)


	def mostrarVideos(self):

		path = os.getcwd() + self.videoDir
		selected = self.app.openBox(title="VideoSelector", dirName=path, fileTypes=[('videos', '*.mp4'), ('videos', '*.mpeg')], asFile=False, parent=None)

		return selected

	def enviarVideo(self):

		users = self.app.getListBox("userList")
		if users:
			user = users[0]
			if user != None:

				videoPath = self.mostrarVideos()
				if videoPath == () or videoPath == "" :
					return 

				infoUser = self.server.getInfoUsuario(user)
				ip = infoUser['ip']
				if self.inCall == True:
					ret = self.app.okBox("ERROR", "Para enviar un video a otro usuario necesitas colgar la videollamada actual", parent=None)

					if ret == False:
						return
					elif ret == True:
						self.colgar()
				
				if ip == None:
					self.app.errorBox("ERROR", "Hay un problema con el usuario: {} .\n No se puede realizar envio".format(user))
					return 

				self.comtcp.send_video_calling(ipDest= ip, portDest= infoUser['listenPort'] , username= self.username, videoPath= videoPath)

			else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")
		else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")


	def userButtons(self, btnName):
		"""
		FUNCION: userButtons(self, btnName)
		ARGS_IN: 
			* btnName: Nombre del boton que se ha pulsado.
		DESCRIPCION:
			Selecciona la funcionalidad del boton correspondiente
		ARGS_OUT:
				-
		"""
		
		if btnName == "Buscar":
			self.buscar()
		elif btnName == "Actualizar":
			self.actualizarUsuarios()
		elif btnName == "Enviar Video":
			self.enviarVideo()
		elif btnName == "Llamar":
			self.llamar()
		elif btnName == "Colgar":
			self.colgar()
		elif btnName == "Play":
			self.play()
		elif btnName == "Pause":
			self.pause()
		elif btnName == "Logout":
			self.logout()


	def setUsersLayout(self):
		"""
		FUNCION: setUsersLayout(self)
		ARGS_IN: 
		DESCRIPCION:
			Muestra la pantalla principal de la aplicacion
		ARGS_OUT:
				-
		"""
		
		self.app.removeAllWidgets()
		self.app.removeStatusbar()
		self.app.setSticky("")
		self.app.setStretch('Both')


		self.app.addImage("logo", self.logo , 0,0, compound = None)

		self.app.addLabelEntry("Busqueda: ", 1, 0)
		self.app.setEntryBg("Busqueda: ", self.listColor)

		self.app.addListBox("userList", self.userList,  2, 0)

		self.videoBox = self.app.addImage("videoBox",self.videoBoxImage , 0, 1, rowspan = 3)

		self.cameraCapture = self.app.addImage("webCamBox", self.webCamBoxImage, 0, 2, rowspan = 10)

		self.app.addLabel("userLabel", "Usuario: {}".format(self.username), 0, 2)
		self.app.setLabelBg("userLabel", self.listColor)


		self.app.addButtons(["Actualizar", "Buscar"], self.userButtons, 3, 0)
		self.app.addButtons(["Llamar", "Colgar", "Play", "Pause"], self.userButtons, 3, 1)

		self.app.addButtons(["Enviar Video"], self.userButtons, 4, 0)

		self.app.addOptionBox("FPS", ["10 FPS", "20 FPS", "30 FPS"], 4, 1)


		self.app.addButtons(["Logout"], self.userButtons, 3, 2)
		self.app.setPollTime(20) 
		
		self.actualizarUsuarios()
		
		# Copypaste, may be useful cuando tengamos que controlar esas cosillas
		self.app.addStatusbar(fields=3)
		self.app.setStatusbarBg(self.bgColor)
		self.app.setStatusbar("FPS=",0)
		self.app.setStatusbar("No current call",1)
		self.app.setStatusbar("...",2)
		

	def setLoginLayout(self):
		"""
		FUNCION: setLoginLayout(self)
		ARGS_IN: 
		DESCRIPCION:
			Muestra la pantalla de login de la aplicacion
		ARGS_OUT:
				-
		"""

		# Initial conf
		self.app.removeAllWidgets()
		self.app.removeStatusbar()
		self.app.setSticky("")
		self.app.setStretch('Both')

		self.app.addImage("logo", self.logo , 0, 0, compound =None)

		self.app.addLabelEntry("Usuario:   ", 1,0  )

		self.app.addLabelSecretEntry("Contraseña:   ", 2, 0)

		self.app.setFocus("Usuario:   ")

		self.app.enableEnter(self.loginButtons)

		self.app.addButtons( ["Login", "Exit"], self.loginButtons, 3, 0,  colspan=1)
