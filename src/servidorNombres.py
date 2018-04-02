import socket

class servidorNombres:

	# Devuelve el socket creado

	def conectarSocket(self):
		puertoServidor = 8000
		nombreSevidor = "vega.ii.uam.es"
		socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		socketCliente.connect((nombreSevidor,puertoServidor))
		return socketCliente

	# Devuelve el puerto del cliente

	def conseguirPuerto(self):
		try:
			with open("client.conf", "r") as f:
				for line in f:
				    port = line.split()[1]
		except EnvironmentError:
			return None

		return port


	def solicitarUsername(self, nick, pwd, socketCliente):
		ip_address = socket.gethostbyname(socket.getfqdn()) # Internet dice que pue fallar pero no se mu bien
		port = self.conseguirPuerto()

		if port == None:
			return None

		mensaje = "REGISTER "+nick+" "+ip_address+" "+port+" "+pwd+" "+" V1"
		socketCliente.send(mensaje)
		respuesta = socketCliente.recv(1024)

		if respuesta == "NOK WRONG_PASS":
			return None

		# Guardamos los datos

		with open("authentication.dat", "w") as f:
			f.write('username '+ nick+'\n')
			f.write('pwd '+ pwd + '\n')

		return "OK"  # DE MOMENTO NO HAGO NA CON EL NICK Y EL TS, HARA FALTA?

	# lo haremos cada vez que un usuario se conecte automaticamente (sin introducir credenciales)
	# obviamente, antes permitirle iniciar sesion automaticamente , si falla, al login
	def renovarUsername(self,socketCliente):
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
		port = self.conseguirPuerto()

		if port == None:
			return None

		mensaje = "REGISTER "+username+" "+ip_address+" "+port+" "+pwd+" "+" V1"
		socketCliente.send(mensaje)
		respuesta = socketCliente.recv(1024)

		if respuesta == "NOK WRONG_PASS":
			return None

		return "OK"

	def getIPUsuario(self, username, socketCliente):
		mensaje = "QUERY " + username
		socketCliente.send(mensaje)
		respuesta = socketCliente.recv(1024)

		if respuesta == "NOK USER_UNKNOWN":
			return None


	def listarUsuarios(self, socketCliente):
		mensaje = "LIST_USERS"
		socketCliente.send(mensaje)
		respuesta = socketCliente.recv(1024)


		if respuesta == "NOK USER_UNKNOWN":
			return None


		#return lista bien formateada (sera llamado desde la gui)

	#def solicitarConexionUsuario(self, username, port):

		# enviamos solicitud CALLING (debe incluir PUERTO RECEPCION VIDEO)
		# esperamos respuesta CALL_ACCEPTED
		# respuesta incluye: OK/NO, PUERTO AL QUE MANDAR VIDEO
		# se inicia la transmision de video

	def cerrarConexion(self, socketCliente):
		mensaje = "QUIT"
		socketCliente.send(mensaje)
		respuesta = socketCliente.recv(1024)
		socketCliente.close()
		return respuesta