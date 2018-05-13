########
# REDES 2 - PRACTICA 3
# FICHERO: comunicacionUDP.py
# DESCRIPCION: Fichero que define las funciones de comunicacion sobre UDP (transmision de video)
# AUTORES: 
#	* Luis Carabe Fernandez-Pedraza 
#	* Emilio Cuesta Fernandez
# LAST-MODIFIED: 13-05-2018
########

import time
import queue
import socket
import cv2
import numpy
from pathlib import Path
from PIL import Image, ImageTk


class comunicacionUDP:
	"""
    CLASE: ComunicacionUDP
    DESCRIPCION: Se encarga de la transmision y recepcion de video por medio 
    				de una comunicacion UDP
    """

    # Referencia al descriptor necesario para capturar frames
	cap = None
	# Referencia a la interfaz grafica
	gui = None


	# ENVIO

	# Socket de envio de video
	sock = None
	# IP destino
	destIp = 0
	# Puerto destino
	destPort = 0

	# Numero de frame enviado
	numOrden = 0
	# FPS de envio
	FPS = 20
	# Resolucion de envio
	resW = 500
	resH = 400
	# Nivel de compresion del frame
	compresion = 50

	# Ruta de video local (si es necesario)
	videoPath = None


	# RECEPCION
	
	# Socket de recepcion de video 
	socketRecepcion = None
	# Buffer para almacenar el video recibido
	bufferRecepcion = None
	
	# Construction, basic 
	def __init__(self, gui, myip, myPort):
		"""
		FUNCION: Constructor del modulo de comunicacion UDP
		ARGS_IN: 
				* gui: Objeto de la interfaz en la que va a actualizar los frames de video
				* myip: IP del usuario de la aplicacion
				* myport: Puerto en el que el usuario desea recibir los frames de video
		DESCRIPCION:
				Construye el objeto
		ARGS_OUT:
				-
		"""
		self.gui = gui
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket envio UDP
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket recepcion UDP
		self.socketRecepcion.settimeout(0.5) # Timeout en el socket de 0.5 segundos
		self.socketRecepcion.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketRecepcion.bind(("0.0.0.0", int(myPort))) # Asociamos el socket de recepcion al puerto correspondiente

		# Cogemos los FPS que haya seleccionado el usuario
		FPS = self.gui.app.getOptionBox("FPS").split(" ")[0]
		self.cambiarFPS(FPS)
		
		# Creamos un buffer que pueda guardar dos segundos de video (priorityQueu, ordena los frames segun el numOrden)
		self.bufferRecepcion = queue.PriorityQueue(self.FPS*2)



	######################################
	######################################
	######################################
	#### FUNCIONES DE ENVIO DE VIDEO #####
	######################################
	######################################
	######################################

	def cambiarFPS(self, valor):
		"""
		FUNCION: cambiarFPS(self, valor)
		ARGS_IN: 
				* valor: numero de FPS
		DESCRIPCION:
				Cambia el parametro de clase FPS (self.FPS)
		ARGS_OUT:
				-
		"""
		if int(valor) > 0:
			self.FPS = int(valor)
		
	
	def cambiarEnviarVideo(self, rutaVideo, hayVideo):
		"""
		FUNCION: cambiarEnviarVideo(self, rutaVideo, hayVideo)
		ARGS_IN: 
				* rutaVideo: ruta del video a enviar
				* hayVideo: flag, 0 si no queremos enviar video
		DESCRIPCION:
				Permite ajustar la ruta del video que queremos enviar
		ARGS_OUT:
				-
		"""
		if hayVideo == 0:
			self.videoPath = None
		else:
			# Comprobamos si existe
			video = Path(rutaVideo)
			if video.is_file():
				self.videoPath = rutaVideo
		return
	
	def configurarSocketEnvio(self, destIp, destPort):
		"""
		FUNCION: configurarSocketEnvio(self, destIp, destPort)
		ARGS_IN: 
				* destIp: IP del usuario al que vamos a enviar video
				* destPort: Puerto UDP del usuario al que vamos a enviar video
		DESCRIPCION:
				Ajusta los parametros de la clase necesarios para enviar video (IP y puerto)
		ARGS_OUT:
				-
		"""
		self.destIp = destIp
		self.destPort = destPort
 
		
	def crearFrameVideo(self):
		"""
		FUNCION: crearFrameVideo(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Coge un frame del medio de video abierto (webcam o video local), lo muestra
				en la gui y lo comprime para ser enviado.
		ARGS_OUT:
				* None: En caso de error o fin de video
				* compFrame: El frame comprimido en caso de exito
		"""

		# Leemos un frame
		ret, frame = self.cap.read()

		# Comprobamos ret y frame, por si ha terminado el video local o si se ha desconectado la camara
		if (frame is None) or (ret == False):
			# Colgamos la llamada
			self.gui.colgar()
			return None

		if self.videoPath is None:
			# Cogemos los FPS que haya seleccionado el usuario (en caso de video local, los fps estan fijos)
			FPS = self.gui.app.getOptionBox("FPS").split(" ")[0]
			# Si han sido cambiados por el usuario, se lo notificamos a nuestro programa
			if int(FPS) != self.FPS:
				self.cambiarFPS(FPS)
		
		# Calculamos los ms necesarios entre frame y frame para que se cumplan los FPS prometidos
		sec_FPS = float(1/self.FPS) # tiempo = (1/fps) (en segundos)
		# Esperamos dicho intervalo de tiempo
		time.sleep(sec_FPS)
			
		# Cambiamos la resolucion del frame, uno para que se adecue a nuestra gui como emisores y otro para el que va a recibir el video
		frameRes = cv2.resize(frame, (200,300))
		frame = cv2.resize(frame, (self.resW,self.resH))
		
		# Enviamos nuestra imagen a la GUI
		cv2_im = cv2.cvtColor(frameRes,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		self.gui.cambiarFrameWebCam(img_tk)
		
		# Comprimimos imagen para enviar por socket
		encode_param = [cv2.IMWRITE_JPEG_QUALITY,self.compresion]
		resultado, compFrame = cv2.imencode('.jpg',frame,encode_param)
		if resultado == False: 
			return None
		compFrame = compFrame.tobytes()
	
		return compFrame    


	def enviarFrameVideo(self, frame):
		"""
		FUNCION: enviarFrameVideo(self, frame)
		ARGS_IN: 
				* frame: frame comprimido a enviar
		DESCRIPCION:
				Envia un frame con su cabecera correspondiente al usuario conectado con nosotros
		ARGS_OUT:
				-
		"""
		# Comprobamos que haya frame
		if frame is None:
			return
		# Creamos la cabecera
		datos = "{}#{}#{}x{}#{}#".format(self.numOrden, time.time(), self.resW, self.resH , self.FPS)
		datos = datos.encode('utf-8')
		datos = bytearray(datos) # Pasamos string a bytes
		datos = datos + frame # Concatenamos con el frame
		# Aumentamos numero de frame y enviamos
		self.numOrden += 1 
		self.sock.sendto(datos, (self.destIp, int(self.destPort)))

	def transmisionWebCam(self, endEvent, pauseEvent):
		"""
		FUNCION: transmisionWebCam(self, endEvent, pauseEvent)
		ARGS_IN: 
				* endEvent: argumento que comunica si el hilo debe terminar (llamada finalizada)
				* pauseEvent: argumento que comunica si el hilo se debe pausar (llamada pausada)
		DESCRIPCION:
				Crea un frame de video comprimido y lo envia al usuario con el que nos estamos comunicando.
		ARGS_OUT:
				-
		"""
		# Comprobamos si debemos enviar video local
		if self.videoPath is not None:
			# Abrimos el fichero de video y ajustamos los fps (usando los originales del video)
			self.cap = cv2.VideoCapture(self.videoPath)
			self.cambiarFPS(self.cap.get(cv2.CAP_PROP_FPS))
		else:
			# Abrimos webcam
			self.cap = cv2.VideoCapture(0)
		
		while not endEvent.isSet():
		
			while pauseEvent.isSet():
				if endEvent.isSet():
					break # Si cuelga mientras esta pausado salimos del estado de pausa
			# Mientras la llamada siga establecida y no pausada, creamos frame y lo enviamos
			frame = self.crearFrameVideo()
			self.enviarFrameVideo(frame)
			

		# Antes de cerrar el hilo, quitamos nuestra imagen de la gui y cerramos todo lo necesario
		frame =  ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		self.pararTransmision()
		return
		
	def pararTransmision(self):
		"""
		FUNCION: pararTransmision(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Cierra todo lo necesario (sockets y capturadora).
		ARGS_OUT:
				-
		"""
		self.sock.close()
		self.socketRecepcion.close()
		self.cap.release()
		cadena = "FPS = " # Cambiamos el statusBar de la gui
		self.gui.app.setStatusbar(cadena,0)




	##########################################
	##########################################
	##########################################
	#### FUNCIONES DE RECEPCION DE VIDEO  ####
	##########################################
	##########################################
	##########################################
						

	def recepcionFrameVideo(self):
		"""
		FUNCION: recepcionFrameVideo(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Coge un frame con su cabecera recibido en el socket de recepcion y lo mete en el buffer de recepcion.
		ARGS_OUT:
				-
		"""

		# Recibimos del socket
		try:
			mensaje, ip = self.socketRecepcion.recvfrom(80000)
		except:
			return # Si salta el timeout, salimos

		# Comprobamos que el paquete recibido sea de quien esperamos
		if ip[0] != self.destIp:
			return

		# Separamos las cabeceras (split[0] = numOrden)
		split = mensaje.split(b"#")
		# Si el buffer esta lleno, perdemos el frame, si no, lo insertamos con sus cabeceras
		if not(self.bufferRecepcion.full()):
			self.bufferRecepcion.put((int(split[0]), mensaje))
		
		return

	def llenarBufferVideo(self, endEvent, pauseEvent):
		"""
		FUNCION: llenarBufferVideo(self, endEvent, pauseEvent)
		ARGS_IN: 
				* endEvent: argumento que comunica si el hilo debe terminar (llamada finalizada)
				* pauseEvent: argumento que comunica si el hilo se debe pausar (llamada pausada)
		DESCRIPCION:
				Extrae frames del socket de recepcion mientras la llamada este activa y los guarda en el buffer 
		ARGS_OUT:
				-
		"""
		while not endEvent.isSet():
		
			while not pauseEvent.isSet():
				self.recepcionFrameVideo()
				if endEvent.isSet():
					break

		return
				
			#	 nOrden = parRecibidos[0]
			#    ts = parRecibidos[1]
			#    res = parRecibidos[2].split("x")
			#    resW = res[0]
			#    resH = res[1]
			#    FPS = parRecibidos[3]
			#    compFrame = parRecibidos[4]


	def mostrarFrame(self):
		"""
		FUNCION: mostrarFrame(self)
		ARGS_IN: 
				-
		DESCRIPCION:
				Saca frames del buffer de recepcion, los descomprime y los muestra en pantalla.
		ARGS_OUT:
				-
		"""	
		if self.bufferRecepcion.empty():
			time.sleep(2) # Si el buffer esta vacio esperamos dos segundos a que se llene un minimo
			return

		mensaje = self.bufferRecepcion.get()[1]
		
		# Separamos la cabecera del frame
		split = mensaje.split(b"#",4)

		# Cabecera:
			# split[0] - numOrden
			# split[1] - ts
			# split[2] - resolucion
			# split[3] - fps
			# split[4] - frame		

		# Cogemos la resolucion (resWxresH) y los fps
		res = split[2].split(b"x")
		resW = int(res[0])
		resH = int(res[1])
		FPS = int(split[3])
		
	
		# Descompresión de los datos, una vez recibidos
		encimg = split[4]
		decimg = cv2.imdecode(numpy.frombuffer(encimg,numpy.uint8), 1)
		
		# Conversión de formato para su uso en el GUI
		frame = cv2.resize(decimg, (resW,resH))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		
		self.gui.cambiarFrameVideo(img_tk)

		
		# Ahora comprobamos como esta de lleno el buffer y calculamos los ms necesarios entre frame y frame para que se cumplan los FPS
		if self.bufferRecepcion.qsize() < (self.FPS): # Menos del 50% del buffer (reducimos los fps a la mitad)
			sec_FPS = float(1/(0.5*FPS)) # tiempo = (1/(0.5*fps)) (en segundos)
			time.sleep(sec_FPS)
			# Actualizamos la gui
			cadena = "FPS = " + str(FPS*0.5)
			self.gui.app.setStatusbar(cadena,0)
		else: 
			sec_FPS = float(1/FPS) # tiempo = (1/fps) (en segundos)
			# Actualizamos la gui
			cadena = "FPS = " + str(FPS)
			self.gui.app.setStatusbar(cadena,0)
			
	def recepcionWebCam(self, endEvent, pauseEvent):
		"""
		FUNCION: recepcionWebCam(self, endEvent, pauseEvent)
		ARGS_IN: 
				* endEvent: argumento que comunica si el hilo debe terminar (llamada finalizada)
				* pauseEvent: argumento que comunica si el hilo se debe pausar (llamada pausada)
		DESCRIPCION:
				Saca frames del socket de recepcion y los muestra en pantalla mientras la llamada este activa.
		ARGS_OUT:
				-
		"""	

		while not endEvent.isSet():
		
			while not pauseEvent.isSet():
				self.mostrarFrame()
				if endEvent.isSet():
					break
			# Si se pausa el video, vaciamos el buffer de recepcion
			while not self.bufferRecepcion.empty():
				try:
					self.bufferRecepcion.get(False)
				except Empty:
					continue
		# Antes de cerrar el hilo, quitamos la imagen del otro usuario de la gui
		frame =  ImageTk.PhotoImage(Image.open(self.gui.videoBoxImage, "r")) 
		self.gui.cambiarFrameVideo(frame)

		return