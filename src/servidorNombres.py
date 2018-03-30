class servidorNombres:

	def solicitarUsername(self):

	# lo haremos cada vez que un usuario se conecte automaticamente (sin introducir credenciales)
	# obviamente, antes permitirle iniciar sesion automaticamente , si falla, al login
	def renovarUsername(self):

	def listarUsuarios(self):
		#return lista bien formateada (sera llamado desde la gui)

	def getIPUsuario(self, username):
		# return IP

	def solicitarConexionUsuario(self, username, port):

		# enviamos solicitud CALLING (debe incluir PUERTO RECEPCION VIDEO)
		# esperamos respuesta CALL_ACCEPTED
		# respuesta incluye: OK/NO, PUERTO AL QUE MANDAR VIDEO
		# se inicia la transmision de video