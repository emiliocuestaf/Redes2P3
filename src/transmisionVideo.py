import cv2

class videoTransmision:

	gui = None

	# Construction, basic 
	def __init__(self, gui):
		self.gui = gui

	# esta funciones estan diseñadas para funcionar en hilos
	def transmisionWebCam(self, username, IP, port):
		cap = cv2.VideoCapture(0)
		while True:
			ret, frame = cap.read()
			self.gui.cambiarFrameVideo(frame)
			# getFrameFrom...
			# comunicacionP2P.enviarFrame()...

#	def getFrameFromWebCam(self)