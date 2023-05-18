import os, time, sys, socket, select, hashlib

def setUpSock(ip:str='127.0.0.1',port:int=6868):
    sckTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sckUDP.bind((ip,port))
    return sckTCP,sckUDP

def encodeCredentials(usr:str,psw:str):
    hashgen = hashlib.sha512()
    hashgen.update(psw.encode('utf8'))
    return usr.encode('utf8')+b' '+hashgen.digest()

def encodeMsg(msg:str,target:str):
    msg=msg.encode('utf8')
    target=target.encode('utf8')
    return b'!msg-'+msg+b' -> '+target

def encodeCreatGrp(grpName:str):
    return b'!create -> '+grpName.encode('utf8')

def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def runClient(ip:str='127.0.0.1',port:int=7070):
    pass

# if __name__ == "__main__": 
#     if len(sys.argv)>3: set_proc_name(sys.argv[3].encode('utf8'))
#     else: set_proc_name(b'Client P7')
#     runClient(sys.argv[1],int(sys.argv[2]))