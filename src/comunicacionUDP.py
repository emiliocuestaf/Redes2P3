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
        #self.sock.bind(("0.0.0.0", int(myPort)))
        self.socketRecepcion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketRecepcion.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketRecepcion.bind(("0.0.0.0", int(myPort)))
        print(int(myPort))
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
        #if ret:
        #    print("holoQUETALANDAMIS")
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
            print('Error al codificar imagen')
            return None
        compFrame = compFrame.tobytes()
        
        #if self.numOrden == 0:
        #    print (compFrame)
    
        return compFrame    


    def enviarFrameVideo(self, frame):
        print("enviarFrame")
        datos = "{}#{}#{}x{}#{}#".format(self.numOrden, time.time(), self.resW, self.resH , self.FPS)
        datos = datos.encode('utf-8')
        datos = bytearray(datos)
        datos = datos + frame
        self.numOrden += 1
        # Num maximo de numOrden?? 
        print("Antes de enviar")
        if self.cliente == True:
            self.sock.sendto(datos, (self.destIp, int(self.destPort)))
            #self.sock.sendto(datos.encode('utf-8'), (self.destIp, int(self.destPort)))
        else: # Se deberia meter aqui???
            #print("Cual es la diferencia" +)
            self.sock.sendto(datos, (self.destIp, int(self.destPort)))
        print("Despues de enviar")

        
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

        #print("Una de caxopito:"+str(self.bufferRecepcion.full()))
    
        while self.bufferRecepcion.full() == False:

            #if self.socketRecepcion is None:
            #    print("willyrex")
            #else:
            #    print("vegeta777")
            print("Antes de recepcion")
            mensaje, ip = self.socketRecepcion.recvfrom(204800) #No se que numero poner, pero si le quitas un 0, no cabe
            print("Despues de recepcion")
            #mensaje = bytearray(mensaje)
            
            #mensaje = mensaje.decode('utf-8')
            
            
            #print("mensaje k koraje")

            #if ip != self.destIp:
            #    print("DEJEN DE ENVIARNOS PAQUETES INDESEADOS")
            #    continue
            
            split = mensaje.split(b"#")
            
            #print("NUMERITO POR AQUI: "+str(split[0]))            
            # Split[0] sera el numOrder, lo que usamos para ordenar la cola
            
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
    
        mensaje = self.bufferRecepcion.get()[1]
        
        split = mensaje.split(b"#",4)
        
        
        #print("Ponme una de bravas:" + str(split[0]) + "\nUna de calamares: "+str(split[1])+"\nUna de jamoncito: "+ str(split[2]) + "\nUna de chipirones: "+str(split[3]))
        
        res = split[2].split(b"x")
        resW = int(res[0])
        resH = int(res[1])
        
        #print("Aqui camarero por favor digame la resolucion: "+str(resW)+" "+str(resH))
    
        #print ("AGUAXIRRI:  "+encimg)
        # Descompresión de los datos, una vez recibidos
        
        # El cuarto parametro del mensaje es la informacion del frame
        encimg = split[4]
        
        #encimg = numpy.array(encimg)
        
        #print(str(encimg))
        
        decimg = cv2.imdecode(numpy.frombuffer(encimg,numpy.uint8), 1)
        
        #if decimg is None:
        #    print("VAmos a ver tú a que jougas")
        
        # Conversión de formato para su uso en el GUI
        
        frame = cv2.resize(decimg, (resW,resH))
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
        
        self.gui.cambiarFrameVideo(img_tk)
        
    
        #cuestiones del formato de imagen y demas aqui
            
    def recepcionWebCam(self, endEvent, pauseEvent):
        
        #print("Wenassss rutilofiolosssss")

        while not endEvent.isSet():

            #print("Pero vamos haber")
        
            while not pauseEvent.isSet():
                #print ("Gallu que deberiamos recibir cosas")
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
                #frame = self.getFrameFromWebCam()
                if endEvent.isSet():
                    break
                
            frame = self.getFrameFromWebCam()
            self.enviarFrameVideo(frame)
            

        
        frame =  ImageTk.PhotoImage(Image.open(self.gui.webCamBoxImage, "r")) 
        self.gui.cambiarFrameWebCam(frame)
        
        self.pararTransmision()
        
        return

