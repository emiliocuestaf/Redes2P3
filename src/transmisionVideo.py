import cv2
from PIL import Image, ImageTk

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
			cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
			img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
			self.gui.cambiarFrameVideo(img_tk)
			# getFrameFrom...
			# comunicacionP2P.enviarFrame()...

#	def getFrameFromWebCam(self)