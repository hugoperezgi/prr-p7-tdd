import os, time, sys, socket, select
import hashlib

def setUpSock(ip: str='127.0.0.1', port: int=6969, mode: int=1):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip,port))
    return s
def setUpUnbindedSock(mode: int=0):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(1)
    return s

def generateAdmin():
    adminUID=b'admin#0000'
    hashgen=hashlib.sha512()
    hashgen.update(adminUID)
    adminPass=hashgen.digest()
    return (adminUID,adminPass)

def setUpStoredGroups():
    grp=set()
    try: 
        f=open("local/groups.bin","xb",0)
        f.close()
    except FileExistsError:
        f=open("local/groups.bin","rb",0)
        ls = f.readlines()
        f.close()
        for l in ls: grp.add(l)

    return grp

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
            registerdUsers[l.partition(b" ")[0]] = l.partition(b" ")[2].strip(b'\n')

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
    groups=setUpStoredGroups()
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
    if shiet != b' ': 
        sck.send(b'Error format should be: name#id password')
        return -1
    uname=unam.partition(b'#')
    if uname[1] != b'#': 
        sck.send(b'Error user must have name#id format')
        return -1
    try: 
        if int(uname[2].decode("utf8").strip())/10000 >= 1: 
            sck.send(b'Error userid must be a 4-digit')
            return -1  
    except ValueError: 
        sck.send(b'Error userid must be a 4-digit')
        return -1  
    
    psw=psw.partition(b'\n')
    while True:
        if psw[1]==b'':break
        psw=psw[0]+psw[2]
        psw=psw.partition(b'\n')  
    psw=psw[0].partition(b'\r')
    while True:
        if psw[1]==b'':break
        psw=psw[0]+psw[2]
        psw=psw.partition(b'\r')
    p=psw[0]

    saveCli(unam,p) 
    LoggedSockets[sck.fileno()]=unam
    ListeningSockets.append(sck)
    RegisteredUsers[unam]=p
    sck.send(b'logedIn')
    return 0

def handleNewConnection(sck:socket.socket,msg:bytes,LoggedSockets:dict,RegisteredUsers:dict,ListeningSockets:list,udpsck:socket.socket,groups):
    a=generateAdmin()
    if msg == b'gokys'+b' '+a[0]+b" "+a[1]+b"\n": 
        for s in LoggedSockets: s.send(b'cy@')
        raise SystemExit
    if sck.fileno() in LoggedSockets: attendQuery(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets,groups,setUpUnbindedSock())
    fuck = msg.partition(b' ')[0]
    if fuck in RegisteredUsers: logInUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)
    else: registerNewUser(sck,msg,LoggedSockets,RegisteredUsers,ListeningSockets)

def logInUser(sck:socket.socket,msg:bytes,LoggedSockets: dict,RegisteredUsers:dict,ListeningSockets:list):
    u,_,p=msg.partition(b' ')

    psw=p.partition(b'\n')
    while True:
        if psw[1]==b'':break
        psw=psw[0]+psw[2]
        psw=psw.partition(b'\n')  
    psw=psw[0].partition(b'\r')
    while True:
        if psw[1]==b'':break
        psw=psw[0]+psw[2]
        psw=psw.partition(b'\r')
    p=psw[0]

    if p == RegisteredUsers[u]:
        LoggedSockets[sck.fileno()]=u
        ListeningSockets.append(sck)
        sck.send(b'logedIn')
        return 0
    else: 
        sck.send(b'urppIsNotBigEnough')
        return 1

def checkIp(ipstr):
    ipstr=b''
    ipstr=ipstr.partition(':')
    if ipstr[1] == b'': return (False,None)
    try: 
        port=int(ipstr[2].decode('utf8').strip())
    except ValueError : return (False,)
    return (True,(ipstr[0].decode('utf8').strip(),port))

def sendPM(msg,toUser,fromUser):
    toUser=toUser.decode('utf8').strip()
    fromUserS=fromUser.decode('utf8').strip()
    thisway=toUser+'_'+fromUserS
    try: f=open("local/"+thisway+".bin","ab",0)
    except FileNotFoundError:
        theotherway=fromUserS+'_'+toUser
        try: f=open("local/"+theotherway+".bin","ab",0)
        except FileNotFoundError:
            f=open("local/"+theotherway+".bin","xb",0)
    f.write(fromUser.partition(b'#')[0]+msg+b'\n')
    f.close()

def sendGrpMsg(msg,toGRP,fromUser):
    toGRP=toGRP.decode('utf8').strip()
    thisway=toGRP+'_group'
    try: f=open("local/"+thisway+".bin","ab",0)
    except FileNotFoundError:
        f=open("local/"+thisway+".bin","xb",0)
    f.write(fromUser.partition(b'#')[0]+msg+b'\n')
    f.close()

def createGrp(name,groups):
    groups.add(name)
    f=open("local/groups.bin","ab",0)
    f.write(name+b"\n")
    f.close()
    f=open("local/"+name.decode('utf8').strip()+"_group.bin","xb",0)
    f.close()
    
def updateChat(sck:socket.socket,msg:bytes,udpsck:socket.socket,ip):
    try:
        try:
            a=msg[0].partition(b"@")
            if a[1] != b'@':
                sck.send(b'NotaValidFormat') 
                raise ValueError
            f=open("local/"+a[2].decode('utf8').strip()+".bin","rb",0)
        except FileNotFoundError:
            try:
                a=a[2].partition(b'_')
                b=a[2]+a[1]+a[0]
                f=open("local/"+b.decode('utf8').strip()+".bin","rb",0)
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
            if(msg[2] in RegisteredUsers): sendPM(msg[0].removeprefix(b'!msg-'),msg[2],LoggedSockets[sck.fileno()])
            elif(msg[2] not in groups): sendGrpMsg(msg[0].removeprefix(b'!msg-'),msg[2],LoggedSockets[sck.fileno()])               
            else: sck.send(b'invalidChatYouDumbfuck')
        elif(msg[0].startswith(b'!create')):
            if(msg[2] in groups): sck.send(b'groupAlreadyExists')
            if msg[2].partition(b'#')[1] == b'#':  sck.send(b'NotaValidGrpName')
            else: 
                createGrp(msg[2],groups)
                sck.send(b'k')
        elif(msg[0].startswith(b'!updatechat')): #!updatechat@<uid/group> -> dirIpUDPsocket(ip:port)
            v,ip=checkIp(msg[2])                 # <user1_user2> (if chat) <grpname_group> (if group)
            if not v: sck.send(b'notAValidIP')
            else:updateChat(sck,msg,udpsck,ip)
        else: sck.send(b'invalidMSGYouDumbfuck')

def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def runServer():
    # ip=input('Ip to party on: ')
    # port=input('Port: ')
    readSockets,updSocket,registeredUsers,loggedSockets,activeGroups=setUpServer()

    while True:
        try:
            rd,_,_=select.select(readSockets,[],[])

            for sck in rd:
                if sck.fileno() not in loggedSockets: 
                    sck,msg=getNewConnection(sck)
                else: msg=sck.recv(8196)
                handleNewConnection(sck,msg,loggedSockets,registeredUsers,readSockets,updSocket,activeGroups)

        except Exception:pass

if __name__ == "__main__": 
    set_proc_name(b'Server P7')
    runServer()
