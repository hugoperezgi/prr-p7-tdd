import os, time, sys, socket
import hashlib

def setUpSock(ip: str='127.0.0.1', port: int=6969, mode: int=1):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip,port))
    return s

def generateAdmin():
    adminUID=b'admin#0000'
    hashgen=hashlib.sha512()
    hashgen.update(adminUID)
    adminPass=hashgen.digest()
    return (adminUID,adminPass)

def setUpStoredPasswords():
    loggedUsers={}
    adminUID,adminPass=generateAdmin()
    try:
        f=open("local/users.bin","xb",0)
        f.write(adminUID+b" "+adminPass+b"\n")    
        loggedUsers[adminUID] = adminPass
        f.close()
    except FileExistsError:
        f=open("local/users.bin","rb",0)
        ls = f.readlines()
        f.close()
        for l in ls: 
            loggedUsers[l.partition(b" ")[0]] = l.partition(b" ")[2]

    return loggedUsers

def saveCli():pass