from srv import *
import unittest

#OBLIGATORIO
    # Cada cliente deberá identificarse al servidor de chat mediante
    #  un nombre; el servidor forzará a que dicha identidad sea única, debiendo
    #  rechazar conexiones de identidades duplicadas.

    # El servidor permanecerá arrancado, aceptando peticiones de clientes, de
    #  forma continua. El sistema de parada del servidor quedará a criterio del
    #  grupo de desarrollo, no teniendo que ver en ningún caso con los clientes
    #  conectados.

    # Al detenerse el servidor, éste deberá informar a sus clientes para que
    #  realicen la oportuna desconexión.

    # El servidor debe permitir la conexión de más de un cliente de forma
    #  simultánea (esto implica que el servidor no debe terminar tras atender
    #  a un cliente).

    # Cliente y servidor configurables.

    # Documentación obligatoria:
    #     Manual usuario
    #     Manual instalacion
    #     Doc de arquitectura
#OPCIONAL
    # Autentificación basada en un sistema de passwords, en ningún
    #  caso guardadas "en texto claro" en ninguna parte.

    # Que el servidor permita la conexión de clientes de otros grupos de
    #  prácticas.

    # Que el cliente sea capaz de conectarse a servidores de otros grupos
    #  de prácticas.

    # Que el servidor sea un demonio según el concepto Unix, con emisión de
    #  mensajes de diagnóstico al syslog del sistema.

    # Funcionar (tanto cliente como servidor) en otro sistema operativo que
    #  disponga de sockets de Internet. Se valorará en particular la
    #  interacción cliente-servidor entre dos sistemas operativos diferentes.

    # Funcionar (tanto cliente como servidor) usando los dos protocolos de
    #  sockets de Internet (TCP y UDP).

    # Almacenamiento de conversaciones: al conectarse un cliente, o mediante
    #  un comando, el servidor le vuelca la conversión desde un punto temporal
    #  especificado de alguna forma.

    # Canales temáticos: al conectarse un cliente primero elige un canal,
    #  y la conversión sólo se produce entre los clientes conectados a dicho
    #  canal.

    # Moderación: comandos especiales de clientes para la creación/borrado de
    #  canales, gestión del histórico de conversaciones (si lo hay),
    #  desconexión de usuarios maleducados, etc.

    # Mensajes privados: un cliente envía un mensaje al servidor, pero dicho
    #  mensaje sólo es para otro cliente en particular.

    # Documentación opcional:
    #     Documento de diseño detallado
    #     Manual de administración

class TestServer(unittest.TestCase):
    
    def test_setUpSock(self):
        ip='127.0.0.1'
        port=6969
        protocol=0
        self.assertIsInstance(setUpSock(ip,port,protocol),socket.socket().__class__)
        
    def test_generateAdmin(self):
        hashgen=hashlib.sha512()
        hashgen.update(b'admin#0000')
        self.assertTupleEqual((b'admin#0000',hashgen.digest()),generateAdmin())    

    def test_setUpStoredPasswords(self):
        expected={}
        a=generateAdmin()
        expected[a[0]]=a[1] + b'\n'
        self.assertDictEqual(expected,setUpStoredPasswords())

        with self.assertRaises(FileExistsError):
            f=open("./local/users.bin","xb",0)

    def test_saveCli(self):
        exp={}
        usr=b'fuck'
        pss=b'me'
        exp[usr]=pss
        self.assertEqual(exp[usr],saveCli(usr,pss))


if __name__ == "__main__": 
    unittest.main()