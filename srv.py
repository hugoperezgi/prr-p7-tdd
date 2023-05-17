import os, time, sys, socket

def setUpSock(ip: str='127.0.0.1', port: int=6969, mode: int=1):
    '''mode 1 = tcp; mode 0 = udp'''
    if mode: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else: s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip,port))
    return s

