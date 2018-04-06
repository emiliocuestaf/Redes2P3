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
import servidorNombres
import transmisionVideo as tvideo

class Gui:

	#files 
	authenticationFile = "authentication.dat"
	logo = "logo.gif"
	videoBoxImage = "callicon.gif"
	webCamBoxImage = "dandelions.gif"
	
	#configuracion de colores
	bgColor = "OrangeRed"
	listColor = "PaleGoldenRod"


	# modulos necesarios (inicializados en constructor)
	server = servidorNombres.servidorNombres()
	tvideo = None

	# widgets
	userList = []

	# webCam management

	webCamEndEvent = None
	webCamThread = None
	

	# videoDisplay management
	videoDisplayThread = None
	

	# flag para saber si estamos en llamada o no
	inCall = False



	# Construction, basic 
	def __init__(self):
    	
		self.app = gui("Login Window", "1000x500")
		self.app.setTitle("Cyder VideoChat")
		self.app.setIcon(self.logo)
		self.app.setBg(self.bgColor)
		self.app.setResizable(canResize=False)
		self.username = None
		self.pwd = None

		self.server = servidorNombres.servidorNombres()
		self.server.inicializacionPuertos()
		self.server.conectarSocket()
		
		self.tvideo = tvideo.videoTransmision(self)
		
		self.app.setStopFunction(self.checkStop)
		
		signal.signal(signal.SIGINT, self.signal_handler)


	def signal_handler(self, signal, frame):
		if self.inCall == True:
				self.colgar()
		sys.exit(0)

		#self.videoDisplayThread = threading.Thread(target = self.tvideo...)
	def checkStop(self):
		
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
			

		state = self.server.confirmarUsername(username, pwd)
		if state == "OK":
			self.setUsersLayout()
			self.username = username
			self.pwd = pwd
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

		state = self.server.solicitarUsername(username , pwd)
		if state == "OK":
			self.username = username
			self.pwd = pwd
			self.setUsersLayout()
		else:
			self.app.errorBox("Error en login", "Intentelo de nuevo")

	def setUsername(username):
		self.username = username

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



	# from : http://code.activestate.com/recipes/578860-setting-up-a-listbox-filter-in-tkinterpython-27/ 
	# refresca automaticamente
	def buscarUsuarios(self):
		search_term = self.app.getEntry("Search:")
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

	def notificacionLLamada(self, user, IP, Port):
		# por implementar
		pass  

	def llamar(self):
		users = self.app.getListBox("userList")
		
		if users:
			user = users[0]
			if user != None:
				ip = self.server.getIPUsuario(user)

				if self.inCall == True:
					ret = self.app.okBox("ERROR", "Para llamar a otro usuario necesitas colgar la videollamada actual", parent=None)

					if ret == False:
						return
					elif ret == True:
						self.colgar()
				
				if ip == None:
					self.app.errorBox("ERROR", "A problem happened while trying to call {}".format(user))
					return 

				self.webCamEndEvent = threading.Event()
				self.webCamThread = threading.Thread(target = self.tvideo.transmisionWebCam, args = (self.webCamEndEvent,)) 
				self.webCamThread.setDaemon(True)
				self.webCamThread.start()

				mensaje = "LLamada al usuario: {} con IP: {} y puerto ... fallida. Funcionalidad por implementar".format(user, ip)
				self.app.warningBox("Not implemented yet", mensaje)

				# solo en el caso de que todo vaya bien...
				self.inCall = True			
			else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")
		else:
				self.app.errorBox("ERROR", "Seleccione un usuario de la lista, por favor")

	
	def colgar(self):
		
		if self.inCall == True:
			self.webCamEndEvent.set()
			self.inCall = False
			self.app.warningBox("Not implemented yet", "Funcionalidad colgar no implementada")
 
			



	def userButtons(self, btnName):
		if btnName == "Search":
			self.buscarUsuarios()
		elif btnName == "RefreshUsers":
			# cambiar esta funcion para que no "busque"
			self.actualizarUsuarios()
		elif btnName == "Logout":
			self.logout()
		elif btnName == "Llamar":
			self.llamar()
		elif btnName == "Colgar":
			self.colgar()
			


	def setUsersLayout(self):
		# Initial conf
		self.app.removeAllWidgets()
		self.app.setSticky("")
		self.app.setStretch('Both')


		self.app.addImage("logo", self.logo , 0,0, compound = None)

		self.app.addLabelEntry("Search: ", 1, 0)
		self.app.setEntryBg("Search: ", self.listColor)

		self.app.addListBox("userList", self.userList,  2, 0)

		self.videoBox = self.app.addImage("videoBox",self.videoBoxImage , 0, 1, rowspan = 3)

		self.cameraCapture = self.app.addImage("webCamBox", self.webCamBoxImage, 0, 2, rowspan = 3)

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
		self.app.setSticky("")
		self.app.setStretch('Both')

		self.app.addImage("logo", self.logo , 0, 0, compound =None)

		self.app.addLabelEntry("Usuario:   ", 1,0  )

		self.app.addLabelSecretEntry("Contraseña:   ", 2, 0)

		self.app.setFocus("Usuario:   ")

		self.app.enableEnter(self.loginButtons)

		self.app.addButtons( ["Login", "Exit"], self.loginButtons, 3, 0,  colspan=1)