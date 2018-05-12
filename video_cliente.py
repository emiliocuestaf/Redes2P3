
import sys

# Importacion del fichero gui, en la carpeta src. Es el unico que necesitamos para iniciar la aplicacion
sys.path.insert(0, './src')
import gui as gui_file


gui = gui_file.Gui()

gui.startGUI()