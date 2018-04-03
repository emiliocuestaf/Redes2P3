import servidorNombres

server = servidorNombres.servidorNombres()

print "Inicializamos puertos"

server.inicializacionPuertos()

print "Conectamos"

server.conectarSocket()

print "Solicitamos Username"

server.solicitarUsername("Luisca", "cr7")

print "HAcemos la pirula"

server.solicitarUsername("Luisca", "cr")

print "Renovamos user"

server.renovarUsername()

print "A ver su ip"

server.getIPUsuario("Luisca")

print "Lista de usuarios"

server.listarUsuarios()

print "Cerramos conexion"

retorno = server.cerrarConexion()

print retorno