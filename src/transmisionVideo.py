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
			frame = cv2.resize(frame, (640,480))
			cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
			img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
			
			self.gui.cambiarFrameVideo(img_tk)

		else:

			self.gui.cambiarFrameVideo("callicon.png")


			# getFrameFrom...
			# comunicacionP2P.enviarFrame()...
	def doSendVideo(self, boolean):
		self.sendVideo = boolean

#	def getFrameFromWebCam(self)