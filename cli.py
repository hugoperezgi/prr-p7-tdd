import os, time, sys, socket, select, hashlib

def setUpSock(ip:str='127.0.0.1',port:int=6868):
    sckTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sckUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sckUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sckUDP.bind((ip,port))
    sckUDP.setblocking(False)
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
    return b'!updatechat@'+grpName.encode('utf8')+b'_group -> '+ipUDP.encode('utf8')+b':'+str(portUDP).encode('utf8')

def encodeUpdateChat(user:str,target:str,ipUDP:str='127.0.0.1',portUDP:int=7070):
    return b'!updatechat@'+user.encode('utf8')+b'_'+target.encode('utf8')+b' -> '+ipUDP.encode('utf8')+b':'+str(portUDP).encode('utf8')

def set_proc_name(newname):
    # pass
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def privateChatSelect(usr:str,sckTCP:socket.socket,udpStuff:tuple):
    #TODO Algo para saber q chats tienes abiertos etc, but no one asked so idc
    os.system('clear')
    target=input("Please introduce the user you want to message: ")
    codedQuery=encodeUpdateChat(usr,target,udpStuff[1],udpStuff[2])
    sckTCP.send(codedQuery)
    socketQueue=[sckTCP,udpStuff[0]]
    rdTRD,_,_=select.select(socketQueue,[],[])
    for sck in rdTRD:
        if(sck.fileno()==socketQueue[1].fileno()):
            data=1
            try:
                while data: 
                    data,_ = sck.recvfrom(2048)
                    print(data.decode('utf8').strip(), end='')
            except BlockingIOError:pass
            print('\n')
            keepChatAlive(usr,target,codedQuery,socketQueue,(usr,sckTCP,udpStuff))
        elif(sck.fileno()==socketQueue[0].fileno()):
            e=sck.recv(2048)
            if e==b'filenotfound': 
                sckTCP.send(encodeMsg('Chat: '+usr+' with '+target+'.\n',target))
                mainMenuArgs=(usr,sckTCP,udpStuff)
                keepChatAlive(usr,target,codedQuery,socketQueue,mainMenuArgs)
            else: 
                print(e.decode('utf8').strip())
                input('Press Intro to continue...')
                mainMenu(usr,sckTCP,udpStuff)

def keepChatAlive(usr:str,trgt:str,codedQuery:bytes,socketQueue:list,mainMenuArgs:tuple):
    socketQueue[0].send(codedQuery)#refresh chat
    socketQueue.append(sys.stdin)    
    while True:

        rdToRead,_,_=select.select(socketQueue,[],[],5)
        for inp in rdToRead:
            if inp.fileno() == socketQueue[1].fileno(): #udp
                data=1
                os.system('clear')
                try:
                    while data:

                        data,_ = inp.recvfrom(2048)
                        print(data.decode('utf8').strip(), end='')
                except BlockingIOError:pass
                print("\n")
            elif inp.fileno() == sys.stdin.fileno(): #i/o
                userInput=inp.readline()
                if userInput == ':q\n': mainMenu(mainMenuArgs[0],mainMenuArgs[1],mainMenuArgs[2])
                elif userInput==':r\n': socketQueue[0].send(codedQuery)
                else: socketQueue[0].send(encodeMsg(usr.partition('#')[0]+': '+userInput,trgt))  
                time.sleep(1)         
                socketQueue[0].send(codedQuery)
            elif inp.fileno() == socketQueue[0].fileno(): #tcp
                r=inp.recv(2048)
                if r == b'cy@':
                    print('The server is shutting down. Closing program...')
                    input('Press Enter to exit.')
                    raise SystemExit
                else:
                    print(r.decode('utf8').strip())
                    input('Press intro to go back to main menu...')
                    mainMenu(mainMenuArgs[0],mainMenuArgs[1],mainMenuArgs[2])
    
def publicGrpSelect(usr:str,sckTCP:socket.socket,udpStuff:tuple):
    os.system('clear')
    target=input("Please introduce the server you want to join: ")
    codedQuery=encodeUpdateGroupChat(target,udpStuff[1],udpStuff[2])
    print('Joining grp, please wait...\n')
    sckTCP.send(codedQuery)
    socketQueue=[sckTCP,udpStuff[0]]
    rdTRD,_,_=select.select(socketQueue,[],[],5)
    for sck in rdTRD:
        if(sck.fileno()==socketQueue[1].fileno()):
            data=1
            try:
                while data: 
                    data,_ = sck.recvfrom(2048)
                    print(data.decode('utf8').strip(), end='')
            except BlockingIOError:pass
            print('\n')
            keepChatAlive(usr,target,codedQuery,socketQueue,(usr,sckTCP,udpStuff))
        elif(sck.fileno()==socketQueue[0].fileno()):
            e=sck.recv(2048)
            if e==b'filenotfound': 
                print(e.decode('utf8').strip())
                input('Press Intro to continue...')
                mainMenu(usr,sckTCP,udpStuff)
            else: 
                print(e.decode('utf8').strip())
                input('Press Intro to continue...')
                mainMenu(usr,sckTCP,udpStuff)
    print('Logged into the chat room.')
    keepChatAlive(usr,target,codedQuery,socketQueue,(usr,sckTCP,udpStuff))


def createGrp(usr:str,sckTCP:socket.socket,udpStuff:tuple):
    os.system('clear')
    target=input("Please introduce the name of the group: ") 
    sckTCP.send(encodeCreatGrp(target.strip('\n')))
    r=sckTCP.recv(2048)
    if r==b'k': print('Group created.')
    else: print(r.decode('utf8').strip())
    input('Press intro to go back into menu.')
    mainMenu(usr,sckTCP,udpStuff)

def mainMenu(usr:str,sckTCP:socket.socket,udpStuff:tuple):

    while True:
        os.system('clear')
        print('Available options:')
        print('1. Select private chat')
        print('2. Select a public group')
        print('3. Create a group')
        print('4. Disconnect')
        sys.stdout.write("Select an option: ")
        sys.stdout.flush()
        r,_,_=select.select([sckTCP,sys.stdin],[],[])

        for i in r:
            if i.fileno() != sys.stdin.fileno(): 
                if i.recv(2048)== b'cy@':
                    print('The server is shutting down. Closing program...')
                    input('Press Enter to exit.')
                    raise SystemExit
            else:
                try: 

                    selectr=int(i.readline())
                    match selectr:
                        case 1:privateChatSelect(usr,sckTCP,udpStuff)
                        case 2:publicGrpSelect(usr,sckTCP,udpStuff)
                        case 3:createGrp(usr,sckTCP,udpStuff)
                        case 4: raise SystemExit
                        case _: print('1,2,3,4')
                except ValueError: print("That's not a number.")
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
        sckTCP.settimeout(10)
        sckTCP.connect((serverIp,serverPort))        
        sckTCP.send(encodeCredentials(usr,psw))
        response=sckTCP.recv(4096)
        if logInResponseLogic(response): continue
        mainMenu(usr,sckTCP,(sckUDP,ip,port))

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
            
