import socket
import time

class servidorDescubrimiento:
	ipAddress = None
	portCliente = None
	portSD = None
	bufferLenght = 1024
	nombreSevidor = "vega.ii.uam.es"
		
	# Construction, basic 
	def __init__(self, portSD, portCliente, publicIpAddress):
		self.portSD = portSD
		self.portCliente = portClient
		self.ipAddress = publicIpAddress

	# Devuelve el socket creado

	def conectarSocket(self):
		if self.portSD == None:
			return None
		socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		socketCliente.connect((self.nombreSevidor,int(self.portSD)))
		return socketCliente

	
	def confirmarUsername(self, username, pwd):
	
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None

		mensaje = "REGISTER "+username+" "+self.ipAddress+" "+self.portCliente+" "+pwd+" "+" V1"
		socketCliente.send(bytes(mensaje, 'utf-8'))
		aux = socketCliente.recv(1024)

		respuesta = aux.decode('utf-8')

		if respuesta == "NOK WRONG_PASS" or respuesta == "NOK SYNTAX_ERROR":
			self.cerrarConexion(socketCliente)
			return None
			
		self.cerrarConexion(socketCliente)

		return "OK"


	def solicitarUsername(self, username, pwd):

		ret = self.confirmarUsername(username, pwd)

		if ret == "OK":

			# Guardamos los datos

			with open("authentication.dat", "w") as f:
				f.write('username '+ username+'\n')
				f.write('pwd '+ pwd + '\n')

			return "OK"  

		return "ERROR"
		

	def getIPUsuario(self, username):
	
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None
	
		mensaje = "QUERY " + username
		socketCliente.send(bytes(mensaje, 'utf-8'))
		aux = socketCliente.recv(1024)

		respuesta = aux.decode('utf-8')

		if respuesta == "NOK USER_UNKNOWN":
			self.cerrarConexion(socketCliente)
			return None

		fields = respuesta.split(" ")
		ip = fields[3]
		
		self.cerrarConexion(socketCliente)
		return ip


	def listarUsuarios(self):
	
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None
		mensaje = "LIST_USERS"
		socketCliente.send(bytes(mensaje, 'utf-8'))

		# El contador sirve para asegurarnos de que leemos todos los usuarios
		aux = socketCliente.recv(self.bufferLenght).decode('utf-8')
		respuesta = aux

		if respuesta == "NOK USER_UNKNOWN":
			self.cerrarConexion(socketCliente)
			return None

		numusers = int(aux.split(" ")[2])

		leidos = aux.count('#')
		while leidos < numusers :

			aux = socketCliente.recv(self.bufferLenght).decode('utf-8')
			#usersAux = aux.split('#')
			#print (usersAux)
			#usersAux = usersAux[:-1]
			#print (usersAux)
			#for userCheck in usersAux:
			#if len(userCheck.split(' ')) != 4:
			#		numusers += numusers;
			leidos += aux.count('#')
			respuesta += aux

		userList = []
		users = respuesta.split("#")
		
		# el primer usuario no esta separado de los primeros mensajes (OK USERS_LIST)
		# se le da un tratamiento distinto
		fields = users[0].split(" ")
		userList.append(fields[3])
		
		# no incluimos el ultimo
		for user in users[1:-1]:
			fields = user.split(" ")
			userList.append(fields[0])

		self.cerrarConexion(socketCliente)
		return userList

	#def solicitarConexionUsuario(self, username, port):

		# enviamos solicitud CALLING (debe incluir PUERTO RECEPCION VIDEO)
		# esperamos respuesta CALL_ACCEPTED
		# respuesta incluye: OK/NO, PUERTO AL QUE MANDAR VIDEO
		# se inicia la transmision de video

	def cerrarConexion(self, socketCliente):
		mensaje = "QUIT"
		socketCliente.send(bytes(mensaje, 'utf-8'))
		respuesta = socketCliente.recv(1024)
		socketCliente.close()
		return respuesta
