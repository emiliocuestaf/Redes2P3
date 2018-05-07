import cv2
import socket
import time
import threading
from PIL import Image, ImageTk
import servidorDescubrimiento as server
import comunicacionUDP as UDP

class ComunicacionTCP:
	"""
    CLASE: ComunicacionTCP
    DESCRIPCION: Se encarga de el envio de comandos via TCP. Estos son, calling, end_call, play, pause, etc.
    			 Tambien se encarga de la recepcion de los mismos
    			 Altamente sincronizada con la clase ComunicacionUDP.
    """

	# Servidor, para conseguir las IP
	server = None
	# Nuestra IP
	publicIP = None
	# Puerto en el que vamos a recibir
	listenPort = None
	# IP del usuario con el que tendremos la comunicacion
	IPdest = None
	# Permanente
	socketRecepcion = None
	# Temporal
	socketEnvio = None	

	# Modulo de comunicacion UDP
	udpcom = None
	# Macros
	queueSize = 5


	# Events para controlar los thread de transmision/recepcion de video por UDP
	pauseEvent = None
	endEvent = None


	waitingVideoAsertion = 0


	# Variables para el thread que mide el tiempo de llamada

	callTimeThread = None

	def __init__(self, gui, myIP, listenPort, serverPort, myUDPport):
		"""
		FUNCION: Constructor del modulo de comunicacion TCP
		ARGS_IN: 
				* gui: Objeto de la interfaz en la que va a actualizar los frames de video
				* myIP: IP del usuario de la aplicacion
				* listenPort: Puerto en el que el usuario escucha comandos de otros usuarios. (Se obtiene del servidor)
				* serverPort: Puerto en el que el sevidor recibe las peticiones sobre otros usuarios (IP, puerto...)
		DESCRIPCION:
				Construye el objeto
		ARGS_OUT:
				-
		"""
		self.gui = gui
		self.listenPort = listenPort
		self.myUDPport = myUDPport
		self.publicIP = myIP
		self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socketRecepcion.bind(('0.0.0.0', int(self.listenPort)))
		self.socketRecepcion.listen(self.queueSize)
		self.server = server.servidorDescubrimiento(serverPort)
		

	# TODO: Borrar esta funcion? SI sirve para algo, esta mal jajajaj
	def close_listeningSocket(self):
		"""
		FUNCION: close_listeningSocket(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Cierra el socket desde el que se escuchaban los comandos de comunicacion P2P
				y las respuestas del servidor.
		ARGS_OUT:
				-
		"""
		self.listenPort.close()

	#### FUNCIONES DE ENVIO DE PETICIONES

	def send_petition(self, ipDest, portDest , petition):
		"""
		FUNCION: send_petition(self, ipDest, portDest , petition)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* petition: Cadena de caracteres que contiene la peticion
		DESCRIPCION:
				Envia peticion a ipDest|portDest
		ARGS_OUT:
				-
		"""

		self.socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(ipDest)
		print(portDest)
		try: 
			self.socketEnvio.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socketEnvio.settimeout(5)
			self.socketEnvio.connect((ipDest, int(portDest)))
			self.socketEnvio.settimeout(None)
		
		except (OSError, ConnectionRefusedError):
			print("No se ha podido establecer una conexion con ese usuario") 
			return "ERROR"

		self.socketEnvio.send(bytes(petition, 'utf-8'))
		self.socketEnvio.close()

	def send_calling(self, ipDest, portDest, myUDPport, username):
		"""
		FUNCION: send_calling(self, ipDest, portDest, myUDPport, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* myUDPPort: Puerto en el que el usuario que envia la peticion recibe video UDP
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion CALLING
		ARGS_OUT:
				-
		"""
		petition = "CALLING {} {}".format(username, myUDPport)
		self.send_petition(ipDest, portDest, petition)

	def send_video_calling(self, ipDest, portDest, myUDPport, username, videoPath):
		"""
		FUNCION: send_calling(self, ipDest, portDest, myUDPport, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* myUDPPort: Puerto en el que el usuario que envia la peticion recibe video UDP
				* username: Nombre del usuario que manda la peticion
				* videoPath: Path del video que se quiere mandar
		DESCRIPCION:
				Envia una peticion CALLING, esta vez orientada a mandar un video
		ARGS_OUT:
				-
		"""
		petition = "CALLING {} {}".format(username, myUDPport)
		self.send_petition(ipDest, portDest, petition)
		self.waitingVideoAsertion = 1

	
	def send_hold(self, ipDest, portDest, username):
		"""
		FUNCION: send_hold(self, ipDest, portDest, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion HOLD, es decir, PAUSE. Y deja de enviar video.
		ARGS_OUT:
				-
		"""
		petition = "CALL_HOLD {}".format(username)
		self.send_petition(ipDest, portDest, petition)
		self.pauseEvent.set()
	

	def send_resume(self, ipDest, portDest, username):
		"""
		FUNCION: send_resume(self, ipDest, portDest, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion RESUME, es decir, PLAY. Y reinicia la trnamision de video.
		ARGS_OUT:
				-
		"""
		petition = "CALL_RESUME {}".format(username)
		self.send_petition(ipDest, portDest, petition)
		self.pauseEvent.clear()

	def send_end(self, ipDest, portDest, username):
		"""
		FUNCION: send_end(self, ipDest, portDest, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion END.  Deja de emitir video y prepara la app para otras posibles llamadas.
		ARGS_OUT:
				-
		"""

		petition = "CALL_END {}".format(username)
		self.send_petition(ipDest, portDest, petition)
		self.endEvent.set()
		self.gui.inCall = False


	#### FUNCIONES DE ENVIO DE RESPUESTAS

	def send_call_accepted(self, ipDest, portDest, myUDPport, username):
		"""
		FUNCION: send_call_accepted(self, ipDest, portDest, myUDPport, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* myUDPPort: Puerto en el que el usuario que envia la rspuesta recibe video UDP
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion CALL_ACCEPTED.
		ARGS_OUT:
				-
		"""	

		petition = "CALL_ACCEPTED {} {}".format(username, myUDPport)
		self.send_petition(ipDest, portDest, petition)
	

	def send_call_denied(self, ipDest, portDest, username):
		"""
		FUNCION: send_call_denied(self, ipDest, portDest, username)
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
				* username: Nombre del usuario que manda la peticion
		DESCRIPCION:
				Envia una peticion CALL_DENIED.
		ARGS_OUT:
				-
		"""	
		petition = "CALL_DENIED {}".format(username)
		self.send_petition(ipDest, portDest, petition)
	

	def send_call_busy(self, ipDest, portDest):
		"""
		FUNCION: send_call_busy(self, ipDest, portDest):
		ARGS_IN: 
				* ipDest: IP del destinatario de la peticion
				* portDest: Puerto en el que el destinatario escucha peticiones
		DESCRIPCION:
				Envia una peticion CALL_BUSY. (Este envio deberia ser automatico)
		ARGS_OUT:
				-
		"""	
		petition = "CALL_BUSY"
		self.send_petition(ipDest, portDest, petition)



	###############################################
	###############################################
	###############################################
	#### FUNCIONES DE RECEPCION DE PETICIONES #####
	###############################################
	###############################################
	###############################################


	def calling_handler(self, username , srcUDPport):
		"""
		FUNCION: calling_handler(self, username , srcUDPport)
		ARGS_IN: 
				* username: Usuario que recibe la peticion
				* srcUDPPort: Puerto en el que el usuario desea recibir el video,
		DESCRIPCION:
				Maneja una peticion de llamada. Pregunta al usuario si quiere aceptarla y remite su respuesta.
				En caso de que el usuario este ocupado, envia BUSY. 
		ARGS_OUT:
				-
		"""	

		print("Estas recibiendo una llamada")

		userInfo = self.server.getInfoUsuario(username)

		if self.gui.inCall == False:

			message = "{} te esta llamando!!! ¿Quieres aceptar?".format(username)
			ret = self.gui.app.yesNoBox("LLamada entrante", message, parent=None)


			if ret == False:

				self.send_call_denied(ipDest = userInfo['ip'], portDest = userInfo['listenPort'] , username = self.gui.username)

			elif ret == True:
				
				self.send_call_accepted(ipDest = userInfo['ip'], portDest = userInfo['listenPort'] , myUDPport =  self.listenPort, username = self.gui.username)					

				self.peerName = username
				self.peerIP = userInfo['ip'] 
				self.peerVideoPort = srcUDPport
				self.peerCommandPort = userInfo['listenPort']


				self.gui.inCall = True
				self.udpcom = UDP.comunicacionUDP( self.gui, self.publicIP, self.myUDPport)
				self.udpcom.configurarSocketEnvio(destIp= userInfo['ip'] , destPort= srcUDPport, cliente= False)
				self.endEvent = threading.Event()
				self.pauseEvent = threading.Event()
				self.webCamThread = threading.Thread(target = self.udpcom.transmisionWebCam, args = (self.endEvent, self.pauseEvent)) 
				self.videoReceptionThread = threading.Thread(target = self.udpcom.recepcionWebCam, args = (self.endEvent, self.pauseEvent)) 
				self.callTimeThread = threading.Thread(target = self.callTimeCount, args = (self.endEvent, self.pauseEvent))


				self.webCamThread.setDaemon(True)
				self.videoReceptionThread.setDaemon(True)
				self.callTimeThread.setDaemon(True)

				# Iniializacion de los threads
				self.webCamThread.start()
				self.videoReceptionThread.start()
				self.callTimeThread.start()

		else:

			self.send_call_busy(ipDest= userInfo['ip'], portDest = userInfo['listenPort'])



	# TODO: En alguna de estas dos funciones, es necesario dejar de recibir frames?? Quiza no porque no se mandan mas

	def call_hold_handler(self, username):
		"""
		FUNCION: call_hold_handler(self, username)
		ARGS_IN: 
				* username: Usuario que recibe la peticion
		DESCRIPCION:
				Maneja una peticion de pausa. Detiene la transmision de frames.
		ARGS_OUT:
				-
		"""	
		if self.gui.inCall == True:


			self.pauseEvent.set()


	def call_resume_handler(self, username):
		"""
		FUNCION: call_resume_handler(self, username)
		ARGS_IN: 
				* username: Usuario que recibe la peticion
		DESCRIPCION:
				Maneja una peticion de play. Reinicia la transmision de frames.
		ARGS_OUT:
				-
		"""	
		if self.gui.inCall == True:

			self.pauseEvent.clear()


	def call_end_handler(self, username):
		"""
		FUNCION: call_end_handler(self, username)
		ARGS_IN: 
				* username: Usuario que recibe la peticion
		DESCRIPCION:
				Maneja una peticion de fin de llamada. Corta la transmision de frames.
		ARGS_OUT:
				-
		"""	
		if self.gui.inCall == True:

			# Con esto dejamos de mandar video
			self.endEvent.set()			
			self.gui.inCall = False	
		
	#### FUNCIONES DE RECEPCION DE RESPUESTAS

	def call_accepted_handler(self, username ,destUDPport):
		"""
		FUNCION: call_accepted_handler(self, username , destUDPport)
		ARGS_IN: 
				* username: Usuario que manda la peticion
				* destUDPPort: Puerto en el que el otro usuario desea recibir el video
		DESCRIPCION:
				Avisa al usuario de que su llamada ha sido aceptada
				Inicia la transmision y recepcion de video con un peer.
		ARGS_OUT:
				-
		"""	

		if self.gui.inCall == False:

			userInfo = self.server.getInfoUsuario(username)

			message = "{} ha aceptado tu llamada!".format(username)
			self.gui.app.infoBox("LLamada establecida", message, parent=None)

			self.gui.inCall = True

			
			self.peerName = username
			self.peerIP = userInfo['ip'] 
			self.peerVideoPort = destUDPport
			self.peerCommandPort = userInfo['listenPort']


			# TODO, ADAPTAR ESTO A CUANDO WAITINGVIDEO VALE 1 (nos confirman que quieren recibir video)
			# acuerdate ademas cambair ese flag a 0 en cuanto se reciba el accepted

			self.udpcom = UDP.comunicacionUDP(self.gui, self.publicIP, self.myUDPport)
			self.udpcom.configurarSocketEnvio(destIp= userInfo['ip'] , destPort= destUDPport, cliente= True)
			self.endEvent = threading.Event()
			self.pauseEvent = threading.Event()
			self.webCamThread = threading.Thread(target = self.udpcom.transmisionWebCam, args = (self.endEvent, self.pauseEvent)) 
			self.videoReceptionThread = threading.Thread(target = self.udpcom.recepcionWebCam, args = (self.endEvent, self.pauseEvent)) 
			self.callTimeThread = threading.Thread(target = self.callTimeCount, args = (self.endEvent, self.pauseEvent))


			self.webCamThread.setDaemon(True)
			self.videoReceptionThread.setDaemon(True)
			self.callTimeThread.setDaemon(True)
			
			self.webCamThread.start()
			self.videoReceptionThread.start()
			self.callTimeThread.start()


		

	def call_denied_handler(self, username):
		"""
		FUNCION: call_denied_handler(self, username)
		ARGS_IN: 
				* username: Usuario que recibe la peticion
		DESCRIPCION:
				Avisa al usuario de que su llamada no ha sido aceptada.
		ARGS_OUT:
				-
		"""	
		message = "{} no ha aceptado tu llamada.".format(username)
		self.gui.app.infoBox("LLamada saliente", message, parent=None)

	def call_busy_handler(self):
		"""
		FUNCION: call_busy_handler(self)
		ARGS_IN: 
		DESCRIPCION:
				Avisa al usuario de que el destinatario su llamada estaba ocupado.
		ARGS_OUT:
				-
		"""	
		message = "El receptor de esta llamada esta ocupado ahora mismo. Intentalo de nuevo mas tarde!"
		self.gui.app.infoBox("LLamada saliente", message, parent=None)

	#### FUNCIONES DE RECEPCION GENERICAS

	def parse_petition(self, text):
		"""
		FUNCION: parse_petition(self, text)
		ARGS_IN: 
				* text: Texto en claro de la peticion recibida.
		DESCRIPCION:
				Parsea la peticion y sus campos y llama al manejador correspondiente con los parametros recibidos.
		ARGS_OUT:
				-
		"""	
		fields = text.split(" ")
		command = fields[0]

		if command == "CALLING":

			self.calling_handler(username= fields[1], srcUDPport= fields[2])
		
		elif command == "CALL_HOLD":

			self.call_hold_handler(username= fields[1])

		elif command == "CALL_RESUME":

			self.call_resume_handler(username= fields[1])

		elif command == "CALL_END":

			self.call_end_handler(username= fields[1])

		elif command == "CALL_ACCEPTED":

			self.call_accepted_handler(username= fields[1], destUDPport= fields[2])

		elif command == "CALL_DENIED":

			self.call_denied_handler(username= fields[1])

		elif command == "CALL_BUSY":

			self.call_busy_handler()



	def listening(self, endEvent):
		"""
		FUNCION: listening(self, endEvent)
		ARGS_IN: 
				* endEvent: event que se utilizara para la finalizacion del thread.
		DESCRIPCION:
				Esta funcion esta diseñada para trabajar en un hilo.
				Esta funcion escucha en el puerto proporcionado en el fichero de configuracion mientras la aplicacion se este ejecutando
				No se debe cerrar antes o no se podran recibir llamadas de otros usuarios
		ARGS_OUT:
				-
		"""	

		while not endEvent.isSet():

			# Asumimos que estos comandos caben en 1024 bytes
			conn, addr = self.socketRecepcion.accept()
			text = conn.recv(1024)

			if text: 

				self.parse_petition(text.decode('utf-8'))


	

	def callTimeCount(self, endEvent, pauseEvent):
		"""
		FUNCION: callTimeCount(self, endEvent, pauseEvent)
		ARGS_IN: 
				* endEvent: event que se utilizara para la finalizacion del thread.
				* pauseEvent: event que se utilizara para parar el cronometro
		DESCRIPCION:
				Esta funcion esta diseñada para trabajar en un hilo.
				Esta funcion actualiza el reloj de tiempo de llamada continuamente.
		ARGS_OUT:
				-
		"""	
		segs = 00
		mins = 00
		hours = 00

		while not endEvent.isSet():

			while pauseEvent.isSet():
				if endEvent.isSet():
					break
			
			time.sleep(1)
			segs += 1
			if segs == 60:
				segs = 0
				mins += 1
				if mins == 60:
					mins = 0
					hours += 1
					if hours == 100:
						hours = 0;

			count = "Tiempo de llamada:       {:02}:{:02}:{:02}".format(hours, mins, segs)
			self.gui.app.setStatusbar(count,1)

		count = "No current call"
		self.gui.app.setStatusbar(count,1)
