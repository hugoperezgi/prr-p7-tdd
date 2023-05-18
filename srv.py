import os, time, sys, socket, select
import hashlib

def setUpSock(ip: str='127.0.0.1', port: int=6969, mode: int=1):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip,port))
    return s
def setUpUnbindedSock(mode: int=1):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s

def generateAdmin():
    adminUID=b'admin#0000'
    hashgen=hashlib.sha512()
    hashgen.update(adminUID)
    adminPass=hashgen.digest()
    return (adminUID,adminPass)

def setUpStoredPasswords():
    registerdUsers={}
    adminUID,adminPass=generateAdmin()
    try:
        f=open("local/users.bin","xb",0)
        f.write(adminUID+b" "+adminPass+b"\n")    
        registerdUsers[adminUID] = adminPass
        f.close()
    except FileExistsError:
        f=open("local/users.bin","rb",0)
        ls = f.readlines()
        f.close()
        for l in ls: 
            registerdUsers[l.partition(b" ")[0]] = l.partition(b" ")[2]

    return registerdUsers

def saveCli(user,passw):
    '''cli user,password saved to local storage'''
    f=open("local/users.bin","ab",0)
    f.write(user+b" "+passw+b"\n")
    f.close()

def setUpServer(ip: str='127.0.0.1', port: int=6969, mode: int=1):
    s=[setUpSock(ip,port,mode),]
    s2=setUpUnbindedSock()
    registerdUsers=setUpStoredPasswords()
    loggedSock={}
    s[0].listen()
    return s,s2,registerdUsers,loggedSock

def getNewConnection(s):
    ns,_=s.accept()
    whateve=ns.recv(8196)
    return ns,whateve

def isNewUser(sck,loggedSock):
    return sck.fileno() not in loggedSock

def registerNewUser(sck:socket.socket,msg: str,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
    unam,shiet,psw=msg.partition(b" ")
    if shiet != b' ': return -1
    uname=unam.partition(b'#')
    if uname[1] != b'#': return -1
    if int(uname[2].decode("utf8").strip())/10000 >= 1: return -1  
    saveCli(unam,psw) 
    LoggedSockets[sck.fileno()]=unam
    ListeningSockets.append(sck)
    RegisteredUsers[unam]=psw
    return 0

def handleNewConnection(sck:socket.socket,msg:str,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
    if sck.fileno() in LoggedSockets: pass #deal with a query
    fuck = msg.partition(b' ')[0]
    if fuck in RegisteredUsers: logInUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)
    else: registerNewUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)

def logInUser(sck:socket.socket,msg: str,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
    u,_,p=msg.partition(b' ')
    if p == RegisteredUsers[u]:
        LoggedSockets[sck.fileno()]=u
        ListeningSockets.append(sck)
        return 0
    else: return 1

def attendQuery():pass
