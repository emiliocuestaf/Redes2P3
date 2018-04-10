import cv2
from PIL import Image, ImageTk

class videoTransmision:

	gui = None

	sendVideo = False

	# Construction, basic 
	def __init__(self, gui):
		self.gui = gui

	

	def getFrameFromWebCam(self, cap):
		ret, frame = cap.read()
		frame = cv2.resize(frame, (200,300))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
		return img_tk

	# esta funciones estan diseñadas para funcionar en hilos
	def transmisionWebCam(self, iniEvent):

		cap = cv2.VideoCapture(0)
		
		while not iniEvent.isSet():

			frame = self.getFrameFromWebCam(cap)
			self.gui.cambiarFrameWebCam(frame)

		
		frame = ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
		self.gui.cambiarFrameWebCam(frame)
		
		cap.release()
		return
		
