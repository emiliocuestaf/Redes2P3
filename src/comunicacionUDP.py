import time
import queue
import socket
import cv2
import numpy
from PIL import Image, ImageTk


class comunicacionUDP:

	
	sock = None
	destIp = 0
	destPort = 0
	numOrden = 0
	FPS = 10
	compresion = 50
	resW = 640
	resH = 480

	localvideo = 0    

	cliente = True
	
	
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
		# Guardamos dos segundos en el buffer
		self.bufferRecepcion = queue.PriorityQueue(self.FPS*1)

	def cambiarEnviarVideo(self, valor):
		if (valor != 0) or (valor != 1):
			return None
		self.localvideo = valor
		
		
	# Cliente es un boolean (True si actuamos como cliente, False si como servidor)
	
	def configurarSocketEnvio(self, destIp, destPort, cliente):
		self.destIp = destIp
		self.destPort = destPort
		self.cliente = cliente

		
	def getFrameFromWebCam(self):
		ret, frame = self.cap.read()
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
		datos = "{}#{}#{}x{}#{}#".format(self.numOrden, time.time(), self.resW, self.resH , self.FPS)
		datos = datos.encode('utf-8')
		datos = bytearray(datos)
		datos = datos + frame
		self.numOrden += 1
		# Num maximo de numOrden?? 
		if self.cliente == True:
			self.sock.sendto(datos, (self.destIp, int(self.destPort)))
		else: # Se deberia meter aqui???
			self.sock.sendto(datos, (self.destIp, int(self.destPort)))

		
	# Reinicia los parametros para poder realizar otra llamada
	def pararTransmision(self):

		self.sock.close()
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

						

	# funcion diseñada para estar en un hilo tol rato
	def recepcionFrameVideo(self):

		if self.bufferRecepcion.empty():
			flag = 1
		else:
			flag = 0

		while flag == 1:

			try:
				mensaje, ip = self.socketRecepcion.recvfrom(204800) #No se que numero poner, pero si le quitas un 0, no cabe
			except:
				break
			
			if ip[0] != self.destIp:
				continue
			
			split = mensaje.split(b"#")
			
			self.bufferRecepcion.put((int(split[0]), mensaje))

			if self.bufferRecepcion.full() == True:
				flag = 0
		
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
			return
	
		mensaje = self.bufferRecepcion.get()[1]
		
		split = mensaje.split(b"#",4)
		
		
		res = split[2].split(b"x")
		resW = int(res[0])
		resH = int(res[1])
		
	
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
		
	
		#cuestiones del formato de imagen y demas aqui
			
	def recepcionWebCam(self, endEvent, pauseEvent):
		

		while not endEvent.isSet():
		
			while not pauseEvent.isSet():
				self.recepcionFrameVideo()
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
		
		
		
	def transmisionWebCam(self, endEvent, pauseEvent):

		self.cap = cv2.VideoCapture(0)
		
		while not endEvent.isSet():
		
			while pauseEvent.isSet():
				if endEvent.isSet():
					break
				
			frame = self.getFrameFromWebCam()
			self.enviarFrameVideo(frame)
			

		
		frame =  ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		
		self.pararTransmision()
		
		return

