class comunicacionP2P:

	gui

	def enviarFrameVideo(self, frame):


	# funcion diseñada para estar en un hilo tol rato
	def recepcionVideo(self, port):
		while True:
			frame = recibirFrameVideo(self, port)
			gui.cambiarFrameGUI(frame)

	def recibirFrameVideo(self, port):
		#cuestiones del formato de imagen y demas aqui
