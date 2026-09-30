import platform
print("🐙 OCTOPOSS INVENTÁRIO")
print("Sistema:", platform.system())
import socket
print("Hostname:", socket.gethostname())
import getpass
print("Usuario:", getpass.getuser())
print("Release:", platform.release())
print("Arquitetura:", platform.machine())
print("Python:", platform.python_version())
import os
print("Diretorio:", os.getcwd())
from datetime import datetime
print("Data/Hora:", datetime.now().astimezone().isoformat())
arquivo = open("evidence/system_inventory.txt", "w", encoding="utf-8")
arquivo.write("=== OCTOPOSS - INVENTARIO DO SISTEMA ===\n")
arquivo.write("Sistema: " + platform.system() + "\n")
arquivo.write("Hostname: " + socket.gethostname() + "\n")
arquivo.write("Usuario: " + getpass.getuser() + "\n")
arquivo.write("Release: " + platform.release() + "\n")
arquivo.write("Arquitetura: " + platform.machine() + "\n")
arquivo.write("Python: " + platform.python_version() + "\n")
arquivo.write("Diretorio: " + os.getcwd() + "\n")
arquivo.write("Data/Hora: " + datetime.now().astimezone().isoformat() + "\n")
