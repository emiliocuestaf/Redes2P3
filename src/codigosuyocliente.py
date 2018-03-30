########
# REDES 2 - PRACTICA 3
# FICHERO: client.py
# DESCRIPCION: Ficheros para probar el funcionamiento de una interfaz
# AUTORES: 
#   * Extraido del git de los profes y modificado por:
#   * Luis Carabe Fernandez-Pedraza 
#   * Emilio Cuesta Fernandez
# LAST-MODIFIED: 20-3-2018
########


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the library
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2

# Hilo dedicado a capturar el stream de OpenCV
frame = []
def hiloCaptura():
    global frame
    cap = cv2.VideoCapture(0)
    while True:
        # Capturamos continuamente los frames de la cámara o del vídeo
        ret, frame = cap.read()
        # La funcion read() es bloqueante y esperará al siguiente frame.
        # Si añadiésemos código aquí, siempre se debería garantizar que
        # ejecuta en menos tiempo de lo que dura el intervalo entre frames.
        # Si no, causa que se llene la cola de OpenCV y se introduzca latencia (lag).

# Función que refresca el frame a mostrar en cada momento en la interfaz
def muestraFrame():
    if len(frame) > 0:
        # Hace una copia del último frame capturado, de paso convirtiéndolo a RGB
        # Efectivamente estamos haciendo "polling" sobre el flujo de vídeo, para poder cambiar de frecuencia de muestreo y FPS.
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        
        # Aquí se podría empaquetar el frame y enviarlo al destinatario
        
        # Lo mostramos en el GUI
        img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))
        app.setImageData("video", img_tk, fmt = 'PhotoImage')

# Función que gestiona los callbacks de los botones
def buttonsCallback(button):
    if button == "Salir":
    	# Salimos de la aplicación
        app.stop()
    elif button == "Conectar":
        # Entrada del nick del usuario a conectar
        nick = app.textBox("Conexión", 
        	"Introduce el nick del usuario a buscar")

# create a GUI variable called app
app = gui("Redes2 - P2P", "640x520")
app.setGuiPadding(10,10)

# add & configure widgets - widgets get a name, to help referencing them later
app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
app.addImage("videoRemoto", "logo.png")

app.startSubWindow("Captura local")
app.addImage("video", "logo.png")
app.stopSubWindow()
app.showSubWindow("Captura local")

# Lanzamos el hilo de captura de vídeo
app.thread(hiloCaptura)

# Registramos la función de representación de video en el interfaz
# Esta misma función también sirve para enviar el vídeo
app.registerEvent(muestraFrame)
app.setPollTime(20) # Esta función la podemos llamar en cualquier momento que queramos cambiar el tiempo entre frames. Es muy útil para el control de flujo.

# Añadir los botones
app.addButtons(["Conectar", "Colgar", "Salir"], buttonsCallback)


# Barra de estado
# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
app.addStatusbar(fields=3)
app.setStatusbar("FPS=",0)
app.setStatusbar("00:00:00",1)
app.setStatusbar("...etc",2)

# Lanza el bucle principal del GUI
app.go()
