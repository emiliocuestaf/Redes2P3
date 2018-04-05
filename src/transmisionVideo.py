import cv2
from PIL import Image, ImageTk

class videoTransmision:

	gui = None
	cap = None

	sendVideo = False

	# Construction, basic 
	def __init__(self, gui, cap):
		self.gui = gui
		self.cap = cap

	# esta funciones estan diseñadas para funcionar en hilos
	def transmisionWebCam(self):

		if self.sendVideo:
			
			ret, frame = self.cap.read()
			frame = cv2.resize(frame, (200,300))
			cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
			img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
			
			self.gui.cambiarFrameWebCam(img_tk)

		else:

			frame =  ImageTk.PhotoImage(Image.open("dandelions.jpg", "r")) 
			self.gui.cambiarFrameWebCam(frame)


			# getFrameFrom...
			# comunicacionP2P.enviarFrame()...
	def doSendVideo(self, boolean):
		self.sendVideo = boolean

#	def getFrameFromWebCam(self)