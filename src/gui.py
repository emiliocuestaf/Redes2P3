from appJar import gui
import tkinter
import cv2
from PIL import Image, ImageTk
import servidorNombres
import transmisionVideo as tvideo
import os
import threading

class Gui:

	authenticationFile = "authentication.dat"
	videoFrame = []
	server = servidorNombres.servidorNombres()
	userList = []
	tvideo = None
	# Construction, basic 
	def __init__(self):
    	
		self.app = gui("Login Window", "1000x500")
		self.app.setTitle("Cyder VideoChat")
		self.app.setIcon("logo.png")
		self.app.setBg("OrangeRed")
		self.app.setResizable(canResize=False)
		self.username = None
		self.pwd = None
		self.server.inicializacionPuertos()
		self.server.conectarSocket()
		cap = cv2.VideoCapture(0)
		self.tvideo = tvideo.videoTransmision(self, cap)

		self.app.registerEvent(self.tvideo.transmisionWebCam)

	def startGUI(self):
		try:
			self.loginFromFile()
		except (EnvironmentError, ValueError):
			self.setLoginLayout()


	def loginFromFile(self): 
		try:
			d = {}
			with open("authentication.dat", "r") as f:
				# Guardamos todos los valores que haya en el fichero
				for line in f:
				    (key, val) = line.split()
				    d[key] = val
		except (EnvironmentError, ValueError):
			raise EnvironmentError("No authentication file")
			
		username = d['username']
		pwd = d['pwd']

		state = self.server.renovarUsername(username, pwd)
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
		self.setLoginLayout()
		
	def loginButtons(self, btnName):
		if btnName == "Exit":
		    self.app.stop()
		if btnName == "Login":
		    self.login()
		  
	def setLoginLayout(self):

		# Initial conf
		self.app.removeAllWidgets()
		self.app.setSticky("")
		self.app.setStretch('Both')

		self.app.addImage("logo", "logo.png" , 0, 0, compound =None)

		self.app.addLabelEntry("Usuario:   ", 1,0  )

		self.app.addLabelSecretEntry("Contraseña:   ", 2, 0)

		self.app.setFocus("Usuario:   ")

		self.app.enableEnter(self.loginButtons)

		self.app.addButtons( ["Login", "Exit"], self.loginButtons, 3, 0,  colspan=1)

		self.app.go()

	def actualizarUsuarios(self):
		
		self.userList = self.server.listarUsuarios()

		self.app.clearListBox("userList", callFunction=True)

		# nos eliminamos de la lista de usuarios a nosotros mismos para evitar problemas
		if self.username != None:
			self.userList.remove(self.username)

		for item in self.userList:
			if item != "":
				self.app.addListItem("userList", item)


	# from : http://code.activestate.com/recipes/578860-setting-up-a-listbox-filter-in-tkinterpython-27/ 
	# refresca automaticamente
	def buscarUsuarios(self):
		search_term = self.app.getEntry("Search:")
		# userList = server.getUsers()
		
		self.app.clearListBox("userList", callFunction=True)

		for item in self.userList:
			if search_term.lower() in item.lower():
				self.app.addListItem("userList", item)

	def cambiarFrameVideo(self, frame):
		self.app.setImageData("videoBox", frame, fmt = 'PhotoImage')

	def notificacionLLamada(self, user, IP, Port):
		# por implementar
		pass  


	def userButtons(self, btnName):
		if btnName == "Search":
			self.buscarUsuarios()
		elif btnName == "RefreshUsers":
			# cambiar esta funcion para que no "busque"
			self.actualizarUsuarios()
		elif btnName == "Logout":
		    self.logout()
		elif btnName == "Llamar":
			users = self.app.getListBox("userList")
			user = users[0]
			
			if user != None:
				self.tvideo.doSendVideo(True)
				ip = self.server.getIPUsuario(user)
				if ip == None:
					self.app.errorBox("ERROR", "AN ERROR OCURRED")
				mensaje = "LLamada al usuario: {} con IP: {} fallida. Funcionalidad por implementar".format(user, ip)
				self.app.errorBox("Not implemented yet", mensaje)
		elif btnName == "Colgar":
			self.tvideo.doSendVideo(False)
			self.app.errorBox("Not implemented yet", "Funcionalidad colgar no implementada")


	def setUsersLayout(self):

		# Initial conf
		self.app.removeAllWidgets()
		self.app.setSticky("")
		self.app.setStretch('Both')


		self.app.addImage("logo", "logo.png" , 0,0, compound = None)

		self.app.addLabelEntry("Search:", 1, 0)

		self.app.addListBox("userList", self.userList,  2, 0)

		userList = self.server.listarUsuarios()
		self.actualizarUsuarios()

		self.videoFrame = self.app.addImage("videoBox","callicon.jpg" , 0, 1, rowspan = 3)

		self.cameraCapture = self.app.addImage("cameraBox", "dandelions.jpg", 0, 2, rowspan = 3)

		self.app.addButtons(["Search", "RefreshUsers"], self.userButtons, 3, 0)

		self.app.addButtons(["Llamar", "Colgar", "Play", "Pause"], self.userButtons, 3, 1)


		self.app.addButtons(["Logout"], self.userButtons, 3, 2)
		self.app.setPollTime(20) # ??
		
		
		# Copypaste, may be useful cuando tengamos que controlar esas cosillas
		#self.app.addStatusbar(fields=3)
		#self.app.setStatusbar("FPS=",0)
		#self.app.setStatusbar("00:00:00",1)
		#self.app.setStatusbar("...etc",2)
		
