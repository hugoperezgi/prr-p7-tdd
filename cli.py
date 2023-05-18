import os, time, sys, socket, select, hashlib

def setUpSock(ip:str='127.0.0.1',port:int=6868):
    sckTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sckUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sckUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

def encodeUpdateGroupChat(grpName:str,ipUDP:str='127.0.0.1',portUDP:int=7070):
    return b'!updatechat@'+grpName.encode('utf8')+b'_group.bin -> '+ipUDP.encode('utf8')+b':'+str(portUDP).encode('utf8')

def encodeUpdateChat(user:str,target:str,ipUDP:str='127.0.0.1',portUDP:int=7070):
    return b'!updatechat@'+user.encode('utf8')+b'_'+target.encode('utf8')+b'.bin -> '+ipUDP.encode('utf8')+b':'+str(portUDP).encode('utf8')

def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def privateChatSelect(usr:str,sckTCP:socket.socket,sckUDP:socket.socket):pass
def publicGrpSelect(usr:str,sckTCP:socket.socket,sckUDP:socket.socket):pass
def createGrp(usr:str,sckTCP:socket.socket):pass

def mainMenu(usr:str,sckTCP:socket.socket,sckUDP:socket.socket):

    while True:
        os.system('cls')
        print('Available options:')
        print('1. Select private chat')
        print('2. Select a public group')
        print('3. Create a group')
        print('4. Disconnect')
        selectr=input("Select an option: ")
        try: 
            selectr=int(selectr)
            match select:
                case 1:privateChatSelect(usr,sckTCP,sckUDP)
                case 2:publicGrpSelect(usr,sckTCP,sckUDP)
                case 3:createGrp(usr,sckTCP)
                case 4: raise SystemExit
                case _: print('Learn how to count. Fucking moron.')
        except ValueError: print('Someone is a dumbfuck')
        input('Press Enter for another go, I believe in you...')


def logInResponseLogic(serverResponse:bytes):
    if(serverResponse==b'urppIsNotBigEnough'): 
        print('Wrong Password.\n') 
        return 1   
    elif(serverResponse==b'Error format should be: name#id password'):
        print('Connection format for log in is spected to be:\n') 
        print(' displayname#id password \n') 
        return 1   
    elif(serverResponse==b'Error user must have name#id format') or (serverResponse==b'Error userid must be a 4-digit'):
        print('User must have a displayname#id format. id has to be a 4-digit integer.\n') 
        return 1   
    else: return 0

def runClient(ip:str='127.0.0.1',port:int=7070,serverIp:str='127.0.0.1',serverPort:int=6969):


    while True:
        usr=input('Username:')
        psw=input('Password:')
        sckTCP,sckUDP=setUpSock(ip,port)
        sckTCP.connect((serverIp,serverPort))        
        sckTCP.send(encodeCredentials(usr,psw))
        response=sckTCP.recv(4096)
        if logInResponseLogic(response): continue
        mainMenu(usr,sckTCP,sckUDP)

if __name__ == "__main__": 
    #python3 cli (clientIp clientPort (serverIp serverPort (processName)))
    if len(sys.argv)>5: 
        set_proc_name(sys.argv[5].encode('utf8'))
        runClient(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))   
    else: 
        set_proc_name(b'Client P7')
        if len(sys.argv)>4:runClient(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
        elif len(sys.argv)>2:runClient(sys.argv[1],int(sys.argv[2]))
        else: runClient()
            
