import cv2
from PIL import Image, ImageTk


class ComunicacionTCP:

	# Campos
	# Temporal
	socketEnvio = None
	# Permanente
	socketRecepcion = None


	# Macros
	queueSize = 5

	# Construction, basic 
	def __init__(self, gui, myip, listenPort):
		self.gui = gui
		self.listenPort = listenPort
		self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverRecepcion.bind((myip, 80))
		self.serverRecepcion.listen(self.queueSize)

		# mala iniciacion del socket de Recepcion, es un poco raro hacer un socket abierto a todo el mundo
		#self.socketRecepcion.connect((ip, int(self.listenPort)))

	# Close socket

	def close_listeningSocket(self):
		self.listenPort.close()


	#### FUNCIONES DE ENVIO DE PETICIONES

	def send_petition(self, ipDest, portDest , petition):
		self.socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socketEnvio.connect((ipDest, int(self.portDest)))
		self.socketEnvio.send(bytes(peticion, 'utf-8'))

	def send_calling(self, ipDest, portDest, myUDPport, username):

		petition = "CALLING {} {}".format(username, myUDPport)
		self.send_petition(self, ipDest, portDest, petition)

	
	def send_hold((self, ipDest, portDest, username):

		petition = "CALL_HOLD {}".format(username)
		self.send_petition(self, ipDest, portDest, petition)
	

	def send_resume(self, ipDest, portDest, username):

		petition = "CALL_RESUME {}".format(username)
		self.send_petition(self, ipDest, portDest, petition)
	

	def send_end(self, ipDest, portDest, username):

		petition = "CALL_END {}".format(username)
		self.send_petition(self,  ipDest, portDest, petition)
	

	#### FUNCIONES DE ENVIO DE RESPUESTAS


	def send_call_accepted(self, ipDest, portDest, myUDPport, username):

		petition = "CALL_ACCEPTED {} {}".format(username, myUDPport)
		self.send_petition(self, ipDest, portDest, petition)
	

	def send_call_denied(self, ipDest, portDest, username):

		petition = "CALL_DENIED {}".format(username)
		self.send_petition(self, ipDest, portDest, petition)
	

	def send_call_busy(self, ipDest, portDest):

		petition = "CALL_BUSY"
		self.send_petition(self, ipdest, portDest, petition)


	#### FUNCIONES DE RECEPCION DE PETICIONES

	def calling_handler(username , srcUDPport):

		message = "{} te esta llamando!!! ¿Quieres verle?".format(username)
		ret = self.gui.yesNoBox("LLamada entrante", message, parent=None)

		if ret == False:

			# get ip and port from username
			# que chapa esta no?

			self.send_call_denied()
		elif ret == True:
			
			#comenzar llamada

	def call_hold_handler(username):
		
		# not implemented 
		if gui.inCall == True:

			# dejar de mandar video UDP sin cortar socket


	def call_resume_handler(username):

		# not implemented 
		if gui.inCall == True:

			# reanudar la transmision UDP

	def call_end_handler(username):

		# not implemented 
		if gui.inCall == True:

			# cierra el socket de transmision de video
			# gui.colgar()
			# no del todo el colgar, me refiero a dejar de mostrar nuestro propio video
			# y a cambiar inCall a 0
			# la cosa es que colgar debera llamar a send_call_end() y eso no tiene que repetirse!

	#### FUNCIONES DE RECEPCION DE RESPUESTASs

	def call_accepted_handler(username , destUDPport):
		message = "{} ha aceptado tu llamada!".format(username)
		self.gui.infoBox("LLamada establecida", message, parent=None)

		# comenzar llamada con username y destUDPport

	def call_denied_handler(username):

		message = "{} no ha aceptado tu llamada.".format(username)
		self.gui.infoBox("LLamada saliente", message, parent=None)

	def call_busy_handler():

		message = "{} esta ocupado ahora mismo. Intentalo de nuevo mas tarde!".format(username)
		self.gui.infoBox("LLamada saliente", message, parent=None)

	#### FUNCIONES DE RECEPCION GENERICAS

	def parse_petition(self, text):
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


	# Diseñada para funcionar en hilo
	# Esta funcion escucha en el puerto proporcionado en el fichero de configuracion mientras la aplicacion se este ejecutando
	# No se debe cerrar antes o no se podran recibir llamadas de otros usuarios
	def read(self, closeEvent):

		while closeEvent.isSet():

		# Asumimos que estos comandos caben en 1024 bytes

			text = self.socketRecepcion.recv(1024)

			if text: 

				self.parse_petition(text.decode('utf-8'))


	
