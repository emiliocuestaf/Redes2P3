import socket

class servidorNombres:
	socketCliente = None
	portCliente = None
	portSD = None

	# Devuelve el puerto del cliente

	def inicializacionPuertos(self):
		d = {}
		try:
			with open("client.conf", "r") as f:
				for line in f:
				    (key, val) = line.split()
				    d[key] = val
		except EnvironmentError:
			return None
		self.portSD = d['portSD']
		self.portCliente = d['portCliente']
		return


	# Devuelve el socket creado

	def conectarSocket(self):
		if (self.portSD == None):
			return None
		nombreSevidor = "vega.ii.uam.es"
		self.socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socketCliente.connect((nombreSevidor,int(self.portSD)))
		return 

	def solicitarUsername(self, nick, pwd):
		ip_address = socket.gethostbyname(socket.getfqdn()) # Internet dice que pue fallar pero no se mu bien
		if (self.portCliente == None):
			return None

		mensaje = "REGISTER "+nick+" "+ip_address+" "+self.portCliente+" "+pwd+" "+" V1"
		self.socketCliente.send(mensaje)
		respuesta = self.socketCliente.recv(1024)

		if respuesta == "NOK WRONG_PASS":
			return None

		# Guardamos los datos

		with open("authentication.dat", "w") as f:
			f.write('username '+ nick+'\n')
			f.write('pwd '+ pwd + '\n')

		return "OK"  # DE MOMENTO NO HAGO NA CON EL NICK Y EL TS, HARA FALTA?

	# lo haremos cada vez que un usuario se conecte automaticamente (sin introducir credenciales)
	# obviamente, antes permitirle iniciar sesion automaticamente , si falla, al login
	def renovarUsername(self):
		try:
			d = {}
			with open("authentication.dat", "r") as f:
				# Guardamos todos los valores que haya en el fichero
				for line in f:
				    (key, val) = line.split()
				    d[key] = val
		except EnvironmentError:
			return None
		username = d['username']
		pwd = d['pwd']
		ip_address = socket.gethostbyname(socket.getfqdn())

		if self.portCliente == None:
			return None

		mensaje = "REGISTER "+username+" "+ip_address+" "+self.portCliente+" "+pwd+" "+" V1"
		self.socketCliente.send(mensaje)
		respuesta = self.socketCliente.recv(1024)

		if respuesta == "NOK WRONG_PASS":
			return None

		return "OK"

	def getIPUsuario(self, username):
		mensaje = "QUERY " + username
		self.socketCliente.send(mensaje)
		respuesta = self.socketCliente.recv(1024)

		if respuesta == "NOK USER_UNKNOWN":
			return None	


	def listarUsuarios(self):
		mensaje = "LIST_USERS"
		self.socketCliente.send(mensaje)
		respuesta = self.socketCliente.recv(1024)


		if respuesta == "NOK USER_UNKNOWN":
			return None


		#return lista bien formateada (sera llamado desde la gui)

	#def solicitarConexionUsuario(self, username, port):

		# enviamos solicitud CALLING (debe incluir PUERTO RECEPCION VIDEO)
		# esperamos respuesta CALL_ACCEPTED
		# respuesta incluye: OK/NO, PUERTO AL QUE MANDAR VIDEO
		# se inicia la transmision de video

	def cerrarConexion(self):
		mensaje = "QUIT"
		self.socketCliente.send(mensaje)
		respuesta = self.socketCliente.recv(1024)
		self.socketCliente.close()
		return respuesta