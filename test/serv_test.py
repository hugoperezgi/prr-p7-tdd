from srv import *
import unittest

#OBLIGATORIO


    # Que el servidor sea un demonio según el concepto Unix, con emisión de
    #  mensajes de diagnóstico al syslog del sistema.

    # Funcionar (tanto cliente como servidor) en otro sistema operativo que
    #  disponga de sockets de Internet. Se valorará en particular la
    #  interacción cliente-servidor entre dos sistemas operativos diferentes.


    # Canales temáticos: al conectarse un cliente primero elige un canal,
    #  y la conversión sólo se produce entre los clientes conectados a dicho
    #  canal.



class TestServer(unittest.TestCase):
    
    def setUp(self) -> None:
        try: os.mkdir('local/')
        except FileExistsError: pass
        self.listenSck,self.updSock,self.registerdUsers,self.loggedSock,self.activeGroups = setUpServer()

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
        self.assertEqual(expected[a[0]],setUpStoredPasswords()[a[0]])

        with self.assertRaises(FileExistsError):
            f=open("./local/users.bin","xb",0)

    def test_saveCli(self):
        exp={}
        usr=b'fuck'
        pss=b'me'
        exp[usr]=pss
        saveCli(usr,pss)
        try1=setUpStoredPasswords()
        self.assertEqual(exp[usr]+b'\n',try1[usr])

    def test_setUpServer(self):
        self.assertIsInstance(self.listenSck[0],socket.socket().__class__)
        self.assertIsInstance(self.updSock,socket.socket().__class__)
        self.assertIsInstance(self.registerdUsers,dict)

    def test_getNewConnection(self):
        temp=setUpUnbindedSock(1)
        temp.connect(('127.0.0.1',6969))
        temp.send(b'hello')
        s,helo=getNewConnection(self.listenSck[0])
        self.assertEqual(b'hello',helo)
        self.assertIsInstance(s,socket.socket().__class__)

    def test_isNewUser(self):
        temp=setUpUnbindedSock(1)
        temp.connect(('127.0.0.1',6969))
        temp.send(b'hello')
        s,_=getNewConnection(self.listenSck[0])
        self.assertTrue(isNewUser(s,self.loggedSock))

    def test_registerNewUser(self):
        temp=setUpUnbindedSock(1)
        temp.connect(('127.0.0.1',6969))
        temp.send(b'hello#2345 shietpassword')
        s,elo=getNewConnection(self.listenSck[0])
        self.assertEqual(registerNewUser(s,elo,self.loggedSock,self.registerdUsers,self.listenSck),0)
        try1=setUpStoredPasswords()
        self.assertEqual(b'shietpassword'+b'\n',try1[b'hello#2345'])

    def test_logInUser(self):
        temp=setUpUnbindedSock(1)
        temp.connect(('127.0.0.1',6969))
        temp.send(b'hello#2345 shietpassword')
        s,elo=getNewConnection(self.listenSck[0])
        registerNewUser(s,elo,self.loggedSock,self.registerdUsers,self.listenSck)
        self.assertFalse(logInUser(s,elo,self.loggedSock,self.registerdUsers,self.listenSck))
        self.assertTrue(s.fileno() in self.loggedSock)

    def test_attendQuery(self):
        pass

if __name__ == "__main__": 
    unittest.main()