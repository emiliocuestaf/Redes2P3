from appJar import gui
from PIL import Image, ImageTk

import tkinter
import cv2
import os
import threading
import time
import signal
import sys

# nuestros ficheros
import servidorDescubrimiento as SD
import transmisionVideo as tvideo
import comunicacionTCP as TCP

class Gui:

	#files 
	authenticationFile = "authentication.dat"
	logo = "logo.gif"
	videoBoxImage = "callicon.gif"
	webCamBoxImage = "dandelions.gif"
	
	#configuracion de colores
	bgColor = "OrangeRed"
	listColor = "LightGrey"

	# objetos de clase necesarios (inicializados en constructor)
	server = None
	tvideo = None
	comtcp = None

	# widgets
	userList = []

	# Thread que escucha comandos
	listeningThread = None

	# Flag para saber si estamos en llamada o no
	inCall = False
	# Datos de la persona con la que se esta hablando
	p2pNick = None
	p2pIP = None
	p2pListenPort = None

	username = None
	pwd = None

	# Construction, basic 
	def __init__(self):
    	
		self.app = gui("Login Window", "1000x500")
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
				    d[key] = val

			self.portSD = d['portSD']
			self.portTCP = d['portTCP']
			self.publicIpAddress = d['IP']
			self.portUDP = d['portUDP']
		except (EnvironmentError, Exception):

			print ("ERROR: El fichero de configuracion no tiene el formato adecuado")
			return 

		
		self.server = SD.servidorDescubrimiento(portSD= self.portSD)
		

		self.tvideo = tvideo.videoTransmision(self)

		self.comtcp = TCP.ComunicacionTCP(gui= self, myIP= self.publicIpAddress, listenPort= self.portTCP, serverPort= self.portSD)

		self.app.setStopFunction(self.checkStop)
		
		signal.signal(signal.SIGINT, self.signal_handler)


	def signal_handler(self, signal, frame):

		if self.inCall == True:
				self.colgar()
		sys.exit(0)

		#self.videoDisplayThread = threading.Thread(target = self.tvideo...)
	
	def checkStop(self):
		
		self.endEvent.set()
		if self.inCall == True:
			self.colgar()
			
		return True


	def startGUI(self):
		try:
			self.loginFromFile()
		except (EnvironmentError, ValueError):
			self.setLoginLayout()
			self.app.go()

	def loginFromFile(self): 

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
			
		state = self.server.confirmarUsername(self.portTCP, self.publicIpAddress, username, pwd)
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
		username = self.app.getEntry("Usuario:   ")
		pwd = self.app.getEntry("Contraseña:   ")

		if username.count('#') != 0 :
			self.app.errorBox("Error en login", "Su usuario no puede contener '#' ni otros caracetres extraños")
			self.app.setEntry("Usuario:   ", "", callFunction=False)
			self.app.setEntry("Contraseña:   ", "", callFunction=False)
			return 

		#self.publicIpAddress
		# arreglar 3er argumento
		state = self.server.solicitarUsername(self.portTCP, None, username , pwd)
		if state == "OK":
			self.username = username
			self.pwd = pwd
			self.setUsersLayout()
		else:
			self.app.errorBox("Error en login", "Intentelo de nuevo")

	def setPwd(pwd):
		self.pwd = pwd

	def logout(self):
		self.username = None
		self.pwd = None
		os.remove(self.authenticationFile)
		
		if self.inCall == True:
			self.colgar()

		self.setLoginLayout()

		
	def loginButtons(self, btnName):
		if btnName == "Exit":
		    self.app.stop()
		if btnName == "Login":
		    self.login()
		  
	def actualizarUsuarios(self):
		
		self.userList = self.server.listarUsuarios()

		self.app.clearListBox("userList", callFunction=True)

		# nos eliminamos de la lista de usuarios a nosotros mismos para evitar problemas
		if self.username != None and self.username != "":
			self.userList.remove(self.username)

		for item in self.userList:
			if item != "":
				self.app.addListItem("userList", item)
				self.app.setListItemBg("userList", item, self.listColor)


	# refresca automaticamente
	def buscarUsuarios(self):
		search_term = self.app.getEntry("Search: ")
		# userList = server.getUsers()
		
		self.app.clearListBox("userList", callFunction=True)

		for item in self.userList:
			if search_term.lower() in item.lower():
				self.app.addListItem("userList", item)
				self.app.setListItemBg("userList", item, self.listColor)


	def cambiarFrameVideo(self, frame):
		self.app.setImageData("videoBox", frame, fmt = 'PhotoImage')

	def cambiarFrameWebCam(self, frame):
		self.app.setImageData("webCamBox", frame, fmt = 'PhotoImage')

	def llamar(self):
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

				print("Estas haciendo una llamada3")
				self.comtcp.send_calling(ipDest= ip, portDest= infoUser['listenPort'] , myUDPport= self.portUDP , username= self.username)
				print("Estas haciendo una llamada34")

			else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")
		else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")

	
	def colgar(self):
		
		if self.inCall == True:
			print(self.p2pIP)
			print(self.p2pListenPort)
			print(self.p2pNick)
			print(self.username)
			self.comtcp.send_end(self.p2pIP, self.p2pListenPort, self.username)
 
	def play(self):
		
		if self.inCall == True:
			self.comtcp.send_resume(self.p2pIP, self.p2pListenPort, self.username)

	def pause(self):
		
		if self.inCall == True:
			self.comtcp.send_hold(self.p2pIP, self.p2pListenPort, self.username)

			
	def userButtons(self, btnName):
		if btnName == "Search":
			self.buscarUsuarios()
		elif btnName == "RefreshUsers":
			self.actualizarUsuarios()
		elif btnName == "Logout":
			self.logout()
		elif btnName == "Llamar":
			self.llamar()
		elif btnName == "Colgar":
			self.colgar()
		elif btnName == "Play":
			self.play()
		elif btnName == "Pause":
			self.pause()


	def setUsersLayout(self):
		# Initial conf
		self.app.removeAllWidgets()
		self.app.removeStatusbar()
		self.app.setSticky("")
		self.app.setStretch('Both')


		self.app.addImage("logo", self.logo , 0,0, compound = None)

		self.app.addLabelEntry("Search: ", 1, 0)
		self.app.setEntryBg("Search: ", self.listColor)

		self.app.addListBox("userList", self.userList,  2, 0)

		self.videoBox = self.app.addImage("videoBox",self.videoBoxImage , 0, 1, rowspan = 3)

		self.cameraCapture = self.app.addImage("webCamBox", self.webCamBoxImage, 0, 2, rowspan = 10)

		self.app.addLabel("userLabel", "Usuario: {}".format(self.username), 0, 2)
		self.app.setLabelBg("userLabel", self.listColor)


		self.app.addButtons(["Search", "RefreshUsers"], self.userButtons, 3, 0)

		self.app.addButtons(["Llamar", "Colgar", "Play", "Pause"], self.userButtons, 3, 1)


		self.app.addButtons(["Logout"], self.userButtons, 3, 2)
		self.app.setPollTime(20) 
		
		self.actualizarUsuarios()
		
		# Copypaste, may be useful cuando tengamos que controlar esas cosillas
		self.app.addStatusbar(fields=3)
		self.app.setStatusbarBg(self.bgColor)
		self.app.setStatusbar("FPS=",0)
		self.app.setStatusbar("00:00:00",1)
		self.app.setStatusbar("...etc",2)
		



	def setLoginLayout(self):

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
