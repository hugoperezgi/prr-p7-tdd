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
    s2.settimeout(1)
    registerdUsers=setUpStoredPasswords()
    loggedSock={}
    groups=set()
    s[0].listen()
    return s,s2,registerdUsers,loggedSock,groups

def getNewConnection(s):
    ns,_=s.accept()
    whateve=ns.recv(8196)
    return ns,whateve

def isNewUser(sck,loggedSock):
    return sck.fileno() not in loggedSock

def registerNewUser(sck:socket.socket,msg:bytes,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
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

def handleNewConnection(sck:socket.socket,msg:bytes,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list,groups):
    a=generateAdmin()
    if msg == b'gokys'+b' '+a[0]+b" "+a[1]+b"\n": raise SystemExit
    if sck.fileno() in LoggedSockets: pass #deal with a query
    fuck = msg.partition(b' ')[0]
    if fuck in RegisteredUsers: logInUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)
    else: registerNewUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)

def logInUser(sck:socket.socket,msg:bytes,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
    u,_,p=msg.partition(b' ')
    if p == RegisteredUsers[u]:
        LoggedSockets[sck.fileno()]=u
        ListeningSockets.append(sck)
        return 0
    else: return 1

def checkIp(ipstr):
    ipstr=b''
    ipstr=ipstr.partition(':')
    if ipstr[1] == b'': return (False,None)
    try: 
        port=int(ipstr[2].decode('utf8').strip())
    except ValueError : return (False,)
    return (True,(ipstr[0].decode('utf8').strip(),port))

def sendMsg(msg,toUser,fromUser):
    toUser=toUser.decode('utf8').strip()
    fromUser=fromUser.decode('utf8').strip()
    thisway=toUser+'_'+fromUser
    try: f=open("local/"+thisway+".bin","ab",0)
    except FileNotFoundError:
        theotherway=fromUser+'_'+toUser
        try: f=open("local/"+theotherway+".bin","ab",0)
        except FileNotFoundError:
            f=open("local/"+theotherway+".bin","xb",0)
    f.write(fromUser.partition(b'#')[0]+msg+b'\n')
    f.close()

def createGrp(name,groups):
    groups.add(name)
    f=open("local/"+name.decode('utf8').strip()+"_group.bin","xb",0)
    f.close()
    
def attendQuery(sck:socket.socket,msg:bytes,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list,groups:set,udpsck:socket.socket): 
    if msg == b'':
        LoggedSockets.pop(sck.fileno())
        ListeningSockets.remove(sck)
        sck.close()
    else:
        msg=msg.partition(b" -> ") # <msg> -> <userid/grpid>
        if(msg[1] != b" -> "): 
            sck.send(b'wrongFormatYouDumbfuck')
        if(msg[0].startswith(b'!msg')): 
            if((msg[2] not in RegisteredUsers) or (msg[2] not in groups)): sck.send(b'invalidChatYouDumbfuck')
            else: 
                sendMsg(msg[0].removeprefix(b'!msg-'),msg[2],LoggedSockets[sck.fileno()])
        elif(msg[0].startswith(b'!create')):
            if(msg[2] in groups): sck.send(b'groupAlreadyExists')
            if msg[2].partition(b'#')[1] == b'#':  sck.send(b'NotaValidGrpName')
            else: createGrp(msg[2],groups)
        elif(msg[0].startswith(b'!updatechat')): #!updatechat@<uid/group> -> dirIpUDPsocket(ip:port)
            v,ip=checkIp(msg[2])
            if not v: sck.send(b'notAValidIP')
            try:
                try:
                    a=msg[0].partition(b"@")
                    if a[1] != b'@':
                        sck.send(b'NotaValidFormat') 
                        raise ValueError
                    f=f=open("local/"+a[2].decode('utf8').strip()+".bin","ab",0)
                except FileNotFoundError:
                    try:
                        a=a[2].partition(b'_')
                        b=a[2]+a[1]
                        f=f=open("local/"+b.decode('utf8').strip()+".bin","ab",0)
                    except FileNotFoundError: sck.send(b'filenotfound')

                    try:
                        udpsck.connect(ip)
                        while True:
                            data = f.read()
                            if data == b'': break
                            udpsck.send(data)
                        f.close()
                    except:sck.send(b'notAValidIP')
            except ValueError:pass
        else: sck.send(b'invalidMSGYouDumbfuck')
