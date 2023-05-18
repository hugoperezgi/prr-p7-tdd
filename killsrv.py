import os, sys, socket, hashlib

servIp = ('127.0.0.1',6969)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(servIp)


adminUID=b'admin#0000'
hashgen=hashlib.sha512()
hashgen.update(adminUID)
adminPass=hashgen.digest()
s.send(b'gokys'+b' '+adminUID+b" "+adminPass+b"\n")
s.close()