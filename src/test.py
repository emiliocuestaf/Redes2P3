import servidorNombres

server = servidorNombres.servidorNombres()

print "Conectamos"

socket = server.conectarSocket()

print "Solicitamos Username"

server.solicitarUsername("Luisca", "cr7", socket)

print "HAcemos la pirula"

server.solicitarUsername("Luisca", "cr", socket)

print "Renovamos user"

server.renovarUsername(socket)

print "A ver su ip"

server.getIPUsuario("Luisca", socket)

print "Lista de usuarios"

server.listarUsuarios(socket)

print "Cerramos conexion"

retorno = server.cerrarConexion(socket)

print retorno