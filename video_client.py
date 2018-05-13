########
# REDES 2 - PRACTICA 3
# FICHERO: video_client.py
# DESCRIPCION: Fichero principal para ejecutar la aplicacion 
# AUTORES: 
#	* Luis Carabe Fernandez-Pedraza 
#	* Emilio Cuesta Fernandez
# LAST-MODIFIED: 01-05-2018
########

import sys

# Importacion del fichero gui, en la carpeta src. Es el unico que necesitamos para iniciar la aplicacion
sys.path.insert(0, './src')
import gui as gui_file


gui = gui_file.Gui()

gui.startGUI()