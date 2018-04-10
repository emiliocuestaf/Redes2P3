import time
import queue


class comunicacionUDP:

	gui
	cap
	
	socketEnvio = None
	destIp = 0
	destPort = 0
	numOrden = 0
	FPS = 30
	compresion = 50
	resW = 640
	resH = 480
	
	
	socketRecepcion = None
	
	bufferRecepcion = None
	
	# Construction, basic 
	def __init__(self, gui, myip, myPort):
		self.gui = gui
		self.listenPort = myPort
		self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.serverRecepcion.bind((myip, myPort))
		# Guardamos dos segundos en el buffer
		self.bufferRecepcion = queue.PriorityQueue(self.FPS*2)
		
	def configurarSocketEnvio(self, destIp, destPort):
		# Comprobar si hay socket ya para cerrarlo??
		self.socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.destIp = destIp
		self.destPort = destPort
		
	def getFrameFromWebCam(self):
		ret, frame = self.cap.read()
		frame = cv2.resize(frame, (self.resW,self.resH))
		
		# Enviamos nuestra imagen a la GUI
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		self.gui.cambiarFrameWebCam(img_tk)
		
		# Comprimimos imagen para enviar por socket
		encode_param = [cv2.IMWRITE_JPEG_QUALITY,self.compresion]
		resultado, compFrame = cv2.imencode('.jpg',frame,encode_param)
		
		if resultado == False: 
			print('Error al codificar imagen')
			return None
		compFrame = compFrame.tobytes()
		
		return compFrame	


	def enviarFrameVideo(self, frame):
	
		datos = self.numOrden+"#"+time.time()+"#"+self.resW+"x"+self.resH+"#"+self.FPS+"#"+frame
		self.numOrden ++ 
		# Num maximo de numOrden?? 
		self.socketEnvio.sendto(datos, (self.destIp, self.destPort)

		
	# Reinicia los parametros para poder realizar otra llamada
	def pararTransmision(self):
		self.numOrden = 0
		self.socketEnvio.close()
		self.socketEnvio = None
		self.destIp = 0
		self.destPort = 0
		self.bufferAux = []
		self.cap.release()

						

	# funcion diseñada para estar en un hilo tol rato
	def recepcionFrameVideo(self):
	
		while self.bufferRecepcion.full() == False:
		
			mensaje, ip = self.socket.recvfrom(2048)
			
			if ipCliente != self.destIp:
				continue
			
			split = mensaje.split("#")
			
			# Split[0] sera el numOrder, lo que usamos para ordenar la cola
			
			self.bufferRecepcion.put((split[0], mensaje))
				
					
				
				#nOrden = parRecibidos[0]
			#	ts = parRecibidos[1]
			#	res = parRecibidos[2].split("x")
			#	resW = res[0]
			#	resH = res[1]
			#	FPS = parRecibidos[3]
			#	compFrame = parRecibidos[4]
				
		
		# Miramos si estamos rellenando el buffer por primera vez
		

	def mostrarFrame(self):
	
		mensaje = self.bufferRecepcion.get()[1]
		
		split = mensaje.split("#")
		
		# El cuarto parametro del mensaje es la informacion del frame
		encimg = split[4]
		
		res = split[2].split("x")
		resW = res[0]
		resH = res[1]
	
		# Descompresión de los datos, una vez recibidos
		
		decimg = cv2.imdecode(np.frombuffer(encimg,np.uint8), 1)
		
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
				
		frame =  ImageTk.PhotoImage(Image.open(self.gui.videoBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		
		return
		
		
		
		
	def transmisionWebCam(self, endEvent, pauseEvent):

		self.cap = cv2.VideoCapture(0)
		
		while not endEvent.isSet():
		
			while pauseEvent.isSet():
				frame = self.getFrameFromWebCam()
				if endEvent.isSet():
					break
				
			frame = self.getFrameFromWebCam()
			self.enviarFrameVideo(frame)
			

		
		frame =  ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		
		self.pararTransmision()
		
		return
