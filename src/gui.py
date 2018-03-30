from appJar import gui
import tkinter
import cv2
from PIL import Image, ImageTk

class Gui:

	authenticationFile = "authentication.dat"
	videoFrame = []
	# Construction, basic 
	def __init__(self):
    	
		self.app = gui("Login Window", "900x500")
		self.app.setTitle("Cyder VideoChat")
		self.app.setIcon("logo.png")
		self.app.setBg("OrangeRed")
		self.app.setResizable(canResize=False)
		self.username = None
		self.pwd = None


	def startGUI(self):
		try:
			self.loginFromFile()
		except (EnvironmentError, ValueError):
			self.setLoginLayout()


	def loginFromFile(self): 
		d = {}
		# Abrimos el fichero de autenticacion, controlando excepciones
		
		with open(self.authenticationFile, "r") as f:
			# Guardamos todos los valores que haya en el fichero
			for line in f:
			    (key, val) = line.split()
			    d[key] = val

		username = d['username']
		pwd = d['pwd']
		state = True
		# state = server.loginRequest(username, pwd)
		if state == True:
			self.setUsersLayout()
			self.app.go()

		else: 
			self.setLoginLayout()
			os.remove(authenticationFile)

	def login(self):
		username = self.app.getEntry("Usuario:   ")
		pwd = self.app.getEntry("Contraseña:   ")
		state = True
		# server.loginRequest(username , pwd)
		if state == True:
			with open(self.authenticationFile, "w") as f:
			    f.write('username '+ username+'\n')
			    f.write('pwd '+ pwd + '\n')

			self.username = username
			self.pwd = pwd
			self.setUsersLayout()

	def logout(self):
		self.username = None
		self.pwd = None
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
		
		# userList = server.getUsers()
		userList = ['Platano', 'Pera', 'Uva', 'Jamon', 'Jesus', 'Zarzamora', 'Mora', 
		'Manzana', 'Sidra', 'Ciruela', 'Caiman', 'Pasion', 'Caribu']

		self.app.clearListBox("userList", callFunction=True)

		for item in userList:
			self.app.addListItem("userList", item)


	# from : http://code.activestate.com/recipes/578860-setting-up-a-listbox-filter-in-tkinterpython-27/ 
	# refresca automaticamente
	def buscarUsuarios(self):
		search_term = self.app.getEntry("Search:")
		# userList = server.getUsers()
		userList = ['Platano', 'Pera', 'Uva', 'Jamon', 'Jesus', 'Zarzamora', 'Mora', 
		'Manzana', 'Sidra', 'Ciruela', 'Caiman', 'Pasion', 'Caribu']

		self.app.clearListBox("userList", callFunction=True)

		for item in userList:
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
			self.app.errorBox("LLamada a " + users[0] + " fallida. Funcionalidad por implementar", "LLamada a " + users[0] + " fallida")
		elif btnName == "Colgar":
			self.app.errorBox("Funcionalidad colgar no implementada", "nope")


	def setUsersLayout(self):

		# Initial conf
		self.app.removeAllWidgets()
		self.app.setSticky("")
		self.app.setStretch('Both')


		self.app.addImage("logo", "logo.png" , 0,0, compound =None)

		# userList = server.getUsers()
		self.app.addLabelEntry("Search:", 1, 0)

		# userList = server.getUsers()
		userList = ['Platano', 'Pera', 'Uva', 'Jamon', 'Jesus', 'Zarzamora', 'Mora', 'Manzana', 'Sidra', 'Ciruela', 'Caiman', 'Pasion', 'Caribu']
		self.app.addListBox("userList", userList,  2, 0)

		self.videoFrame = self.app.addImage("videoBox","callicon.png" , 0, 1, colspan = 3 , rowspan = 3)

		self.app.addButtons(["Search", "RefreshUsers", "Llamar", "Colgar", "Logout"], self.userButtons, 3, 0, colspan = 2)

		# Copypaste, may be useful cuando tengamos que controlar esas cosillas
		#self.app.addStatusbar(fields=3)
		#self.app.setStatusbar("FPS=",0)
		#self.app.setStatusbar("00:00:00",1)
		#self.app.setStatusbar("...etc",2)
		
