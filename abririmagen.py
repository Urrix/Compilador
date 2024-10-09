import subprocess

# Ruta de la imagen en Windows
image_path = r'C:\Users\luisa\Documents\Semestre 2023\compiladores\proyecto\syntax_tree.png'

# Abrir la imagen con la aplicación predeterminada en Windows
subprocess.run(['cmd', '/c', 'start', '', image_path], shell=True)
