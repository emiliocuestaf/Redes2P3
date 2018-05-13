########
# REDES 2 - PRACTICA 3
# FICHERO: servidorDescubrimiento.py
# DESCRIPCION: Fichero que define las funciones necesarias para conectar con el servidor de descubrimiento
# AUTORES: 
#	* Luis Carabe Fernandez-Pedraza 
#	* Emilio Cuesta Fernandez
# LAST-MODIFIED: 01-05-2018
########

import socket
import time

class servidorDescubrimiento:

	"""
    CLASE: servidorDescubrimiento
    DESCRIPCION: 
    	Se encarga de las conexiones con el servidor de descubrimiento, que nos sirve 
    	principalmente para inciar sesion y conseguir informacion sobre los usuarios
    """

    # Puerto del servidor
	portSD = None

	# Tamanio del buffer de recepcion
	bufferLenght = 1024

	# Nombre (direccion) del servidor
	nombreSevidor = "vega.ii.uam.es"
		
	# Construction, basic 
	def __init__(self, portSD):
		"""
		FUNCION: Constructor del modulo de comunicacion con el SD
		ARGS_IN: 
				* portSD: Puerto al cual debemos conectarnos
		DESCRIPCION:
				Construye el objeto
		ARGS_OUT:
				-
		"""
		self.portSD = portSD

	def conectarSocket(self):
		"""
		FUNCION: conectarSocket(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Crea un socket TCP que conecta con el servidor de descubrimiento
		ARGS_OUT:
				* socketCliente : el socket creado
				* None : si el puerto no es valido
		"""
		if self.portSD == None:
			return None
		try:
			socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socketEnvio.settimeout(5)
			socketCliente.connect((self.nombreSevidor,int(self.portSD)))
		except (OSError, ConnectionRefusedError):
			return None

		return socketCliente

	
	def confirmarUsername(self, portCliente, IpAddress, username, pwd):
		"""
		FUNCION: confirmarUsername(self, portCliente, IpAddress, username, pwd)
		ARGS_IN: 
				* portCliente: Puerto del cliente que esta iniciando sesion/registrandose
				* IpAddress: Direccion IP del cliente que esta iniciando sesion/registrandose
				* username: Nombre del usuario que esta iniciando sesion/registrandose
				* pwd: Contrasenia del usuario que esta iniciando sesion/registrandose
		DESCRIPCION:
				Envia solicitud al SD de registro de usuario, en caso de que exista,
				comprueba que haya insertado bien la contrasenia, en caso de que no exista,
				lo registra en el servidor
		ARGS_OUT:
				* None: ha habido un problema en la peticion o la contrasenia es incorrecta
				* "OK": el usuario se ha registrado correctamente
		"""

		# Conectamos con el servidor
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None
		try:
			# Creamos la peticion y la enviamos con el formato adecuado
			mensaje = "REGISTER {} {} {} {} V1".format(username, IpAddress, portCliente, pwd)
			socketCliente.send(bytes(mensaje, 'utf-8'))

			# Recibimos la respuesta y comprobamos la cadena devuelta, cerrando la conexion con el socket
			aux = socketCliente.recv(self.bufferLenght)
			respuesta = aux.decode('utf-8')
		except:
			return None

		if respuesta == "NOK WRONG_PASS" or respuesta == "NOK SYNTAX_ERROR":
			self.cerrarConexion(socketCliente)
			return None
			
		self.cerrarConexion(socketCliente)

		return "OK"


	def solicitarUsername(self, portCliente, IpAddress, username, pwd):
		"""
		FUNCION: solicitarUsername(self, portCliente, IpAddress, username, pwd)
		ARGS_IN: 
				* portCliente: Puerto del cliente que esta iniciando sesion/registrandose
				* IpAddress: Direccion IP del cliente que esta iniciando sesion/registrandose
				* username: Nombre del usuario que esta iniciando sesion/registrandose
				* pwd: Contrasenia del usuario que esta iniciando sesion/registrandose
		DESCRIPCION:
				Envia solicitud al SD de registro de usuario, en caso de que exista, comprueba que haya 
				insertado bien la contrasenia, en caso de que no exista, lo registra en el servidor, 
				ademas, guarda los datos del usuario en el fichero de autenticacion.
		ARGS_OUT:
				* "ERROR": ha habido un problema en la peticion o la contrasenia es incorrecta
				* "OK": el usuario se ha registrado correctamente y se han guardado sus datos
		"""
		ret = self.confirmarUsername(portCliente, IpAddress, username, pwd)

		if ret == "OK":

			# Guardamos los datos

			with open("authentication.dat", "w") as f:
				f.write('username '+ username+'\n')
				f.write('pwd '+ pwd + '\n')

			return "OK"  

		return "ERROR"
		

	def getInfoUsuario(self, username):
		"""
		FUNCION: getInfoUsuario(self, username)
		ARGS_IN: 
				* username: Nombre del usuario del que se requiere la informacion
		DESCRIPCION:
				Envia peticion al SD de informacion sobre un usuario y la devuelve en el caso que haya.
		ARGS_OUT:
				* None: ha habido un problema en la conexion o no existe el usuario
				* infoDict: informacion del usuario (username, ip, puerto, version de protocolo)
		"""

		# Conectamos con el servidor
	
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None

		try:
			# Creamos la peticion y la enviamos
			mensaje = "QUERY " + username
			socketCliente.send(bytes(mensaje, 'utf-8'))

			# Recibimos la respuesta y comprobamos la cadena devuelta, cerrando la conexion con el socket
			aux = socketCliente.recv(self.bufferLenght)
			respuesta = aux.decode('utf-8')
		except:
			return None
		self.cerrarConexion(socketCliente)

		# No existe el usuario
		if respuesta == "NOK USER_UNKNOWN":
			return None

		# Creamos una estructura (diccionario) con la informacion recibida
		fields = respuesta.split(" ")

		infoDict = {}
		infoDict['username'] = fields[2]
		infoDict['ip'] = fields[3]
		infoDict['listenPort'] = fields[4]
		infoDict['protocols'] = fields[5]
		
		return infoDict


	def listarUsuarios(self):		
		"""
		FUNCION: listarUsuarios(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Envia peticion al SD para recibir la lista de usuarios registrados.
		ARGS_OUT:
				* None: ha habido un problema en la conexion o en la peticion
				* userList: lista con los nombres de los usuarios registrados
		"""

		# Conectamos con el servidor
	
		socketCliente = self.conectarSocket()

		if socketCliente == None:
			return None
		try:
			# Creamos la peticion y enviamos
			mensaje = "LIST_USERS"
			socketCliente.send(bytes(mensaje, 'utf-8'))

			# Recibimos la respuesta que guardamos en aux
			aux = socketCliente.recv(self.bufferLenght).decode('utf-8')
		except:
			return None
		respuesta = aux

		if respuesta == "NOK USER_UNKNOWN":
			self.cerrarConexion(socketCliente)
			return None

		numusers = int(aux.split(" ")[2])

		# El contador (leidos) sirve para asegurarnos de que leemos todos los usuarios
		leidos = aux.count('#')
		while leidos < numusers :
			# Seguimos leyendo del socket hasta que no queden usuarios por leer
			aux = socketCliente.recv(self.bufferLenght).decode('utf-8')
			leidos += aux.count('#')
			respuesta += aux

		# Separamos todos los usuarios leidos
		userList = []
		users = respuesta.split("#")
		
		# El primer usuario no esta separado de los primeros mensajes (OK USERS_LIST)
		# se le da un tratamiento distinto
		fields = users[0].split(" ")
		userList.append(fields[3]) # Cogemos el nombre del usuario
		
		# No incluimos el ultimo
		for user in users[1:-1]:
			fields = user.split(" ")
			userList.append(fields[0]) # Cogemos el nombre del usuario

		self.cerrarConexion(socketCliente)
		return userList

	def cerrarConexion(self, socketCliente):
		"""
		FUNCION: cerrarConexion(self, socketCliente)
		ARGS_IN: 
				* socketCliente: socket abierto del SD que vamos a cerrar
		DESCRIPCION:
				Envia peticion al SD para cerrar la conexion, despues cierra el socket
		ARGS_OUT:
				* respuesta: respuesta del SD a la peticion QUIT
		"""
		# Enviamos peticion y cerramos socket
		mensaje = "QUIT"
		try:
			socketCliente.send(bytes(mensaje, 'utf-8'))
			respuesta = socketCliente.recv(self.bufferLenght)
			socketCliente.close()
		except:
			return None
		return respuesta
