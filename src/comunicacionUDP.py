import time
import queue
import socket
import cv2
import numpy
from pathlib import Path
from PIL import Image, ImageTk


class comunicacionUDP:

	
	sock = None
	destIp = 0
	destPort = 0
	numOrden = 0
	FPS = 20
	compresion = 50
	resW = 500
	resH = 400

	cap = None
	gui = None
	
	videoPath = None

	
	
	socketRecepcion = None
	
	bufferRecepcion = None
	
	# Construction, basic 
	def __init__(self, gui, myip, myPort):
		self.gui = gui
		self.listenPort = myPort
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketRecepcion.settimeout(0.5)
		self.socketRecepcion.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketRecepcion.bind(("0.0.0.0", int(myPort)))
		# Cogemos los FPS que haya seleccionado el usuario
		FPS = self.gui.app.getOptionBox("FPS").split(" ")[0]
		
		print(str(FPS))
		
		self.cambiarFPS(FPS)
		
		# Guardamos dos segundos en el buffer
		self.bufferRecepcion = queue.PriorityQueue(self.FPS*2)

	def cambiarFPS(valor):
		if int(valor) > 0:
			self.FPS = int(valor)
			cadena = "FPS = " + str(self.FPS)
			self.gui.app.setStatusbar(cadena,0)
		if self.cap is not None:
			self.cap.set(cv2.CAP_PROP_FPS, self.FPS)



	# Si envia None, pasa a modo camara
	
	def cambiarEnviarVideo(self, rutaVideo, hayVideo):
		if hayVideo == 0:
			self.videoPath = None
			return
		# Comprobamos si existe
		video = Path(rutaVideo)
		if video.is_file():
			self.videoPath = rutaVideo
		return
		
		
	# Cliente es un boolean (True si actuamos como cliente, False si como servidor)
	
	def configurarSocketEnvio(self, destIp, destPort):
		self.destIp = destIp
		self.destPort = destPort
 
		
	def crearFrameVideo(self):
		ret, frame = self.cap.read()
		
		# Cogemos los FPS que haya seleccionado el usuario
		FPS = self.gui.app.getOptionBox("FPS").split(" ")[0]
		if int(FPS) != self.FPS:
			self.cambiarFPS(FPS)
		
		sec_FPS = float(1/self.FPS)*1000 # Pasamos a ms
		cv2.waitKey(sec_FPS) #Con esto ajustamos FPS
		if (frame is None) or (ret == False):
			self.gui.colgar()
			return None
			
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
		if frame is None:
			return
		datos = "{}#{}#{}x{}#{}#".format(self.numOrden, time.time(), self.resW, self.resH , self.FPS)
		datos = datos.encode('utf-8')
		datos = bytearray(datos)
		datos = datos + frame
		self.numOrden += 1
		# Num maximo de numOrden?? 
		self.sock.sendto(datos, (self.destIp, int(self.destPort)))


		
	# Reinicia los parametros para poder realizar otra llamada
	def pararTransmision(self):

		self.sock.close()
		self.socketRecepcion.close()
		self.numOrden = 0
		self.sock = None
		self.destIp = 0
		self.destPort = 0
		while not self.bufferRecepcion.empty():
			try:
				self.bufferRecepcion.get(False)
			except Empty:
				continue
			self.bufferRecepcion.task_done()
		self.cap.release()
		cadena = "FPS = "
		self.gui.app.setStatusbar(cadena,0)
						

	# funcion diseñada para estar en un hilo tol rato
	def recepcionFrameVideo(self):
	
		try:
			mensaje, ip = self.socketRecepcion.recvfrom(204800) #No se que numero poner, pero si le quitas un 0, no cabe
		except:
			return
		if ip[0] != self.destIp:
			return
		
		split = mensaje.split(b"#")
		
		# Si el buffer esta lleno, perdemos el frame
		if not(bufferRecepcion.full()):
			self.bufferRecepcion.put((int(split[0]), mensaje))
		
		return    
				
				#nOrden = parRecibidos[0]
			#    ts = parRecibidos[1]
			#    res = parRecibidos[2].split("x")
			#    resW = res[0]
			#    resH = res[1]
			#    FPS = parRecibidos[3]
			#    compFrame = parRecibidos[4]


	def mostrarFrame(self):

		if self.bufferRecepcion.empty():
			cv2.waitKey(1000) # Si esta vacio esperamos un segundo
			return
	
		mensaje = self.bufferRecepcion.get()[1]
		
		split = mensaje.split(b"#",4)
		
		
		res = split[2].split(b"x")
		resW = int(res[0])
		resH = int(res[1])
		FPS = int(split[3])
		
	
		# Descompresión de los datos, una vez recibidos
		
		# El cuarto parametro del mensaje es la informacion del frame
		encimg = split[4]
		
		#encimg = numpy.array(encimg)
		
		decimg = cv2.imdecode(numpy.frombuffer(encimg,numpy.uint8), 1)
		
		# Conversión de formato para su uso en el GUI
		
		frame = cv2.resize(decimg, (resW,resH))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		
		self.gui.cambiarFrameVideo(img_tk)
		
		# Ahora comprobamos como esta de lleno el buffer
		if bufferRecepcion.qsize() < (self.FPS): # Menos del 50% del buffer 
			sec_FPS = float(1/(0.5*self.FPS))*1000 # Pasamos a ms reduciendo FPS  a la mitad
			cv2.waitKey(sec_FPS) #Con esto ajustamos FPS
		else: 
			sec_FPS = float(1/self.FPS)*1000 # Pasamos a ms reduciendo FPS  a la mitad
			cv2.waitKey(sec_FPS) #Con esto ajustamos FPS
		
	
		#cuestiones del formato de imagen y demas aqui
			
	def recepcionWebCam(self, endEvent, pauseEvent):
		

		while not endEvent.isSet():
		
			while not pauseEvent.isSet():
				self.mostrarFrame()
				if endEvent.isSet():
					break

			while not self.bufferRecepcion.empty():
				try:
					self.bufferRecepcion.get(False)
				except Empty:
					continue
		
		frame =  ImageTk.PhotoImage(Image.open(self.gui.videoBoxImage, "r")) 
		self.gui.cambiarFrameVideo(frame)

		return
		
			
	def llenarBufferVideo(self, endEvent, pauseEvent):

		while not endEvent.isSet():
		
			while not pauseEvent.isSet():
				self.recepcionFrameVideo()
				if endEvent.isSet():
					break

		return
		
		
		
	def transmisionWebCam(self, endEvent, pauseEvent):

		if self.videoPath is not None:
			self.cap = cv2.VideoCapture(self.videoPath)
			self.cambiarFPS(video.get(cv2.CAP_PROP_FPS))
		else:
			self.cap = cv2.VideoCapture(0)
		
		while not endEvent.isSet():
		
			while pauseEvent.isSet():
				if endEvent.isSet():
					break
				
			frame = self.crearFrameVideo()
			self.enviarFrameVideo(frame)
			

		
		frame =  ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		
		self.pararTransmision()
		
		return

