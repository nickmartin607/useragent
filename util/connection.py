#!/usr/bin/env python
import socket, ssl
from traceback import print_exception


DEFAULT_ADDR_FAMILY = socket.AF_INET            # IPv4
DEFAULT_SOCKET_TYPE = socket.SOCK_STREAM        # TCP
DEFAULT_SSL_PROTOCOL = ssl.PROTOCOL_SSLv23
DEFAULT_SOCKET_TIMEOUT = 5                      # 5 Seconds
DEFAULT_BUFFER_SIZE = 2048                      # 2 megabytes


class Connection(object):
    def __init__(self, addr, *args, **kwargs):
        self.addr = addr
        self.secure = kwargs.get('secure', False)
        self.protocol = kwargs.get('protocol', DEFAULT_SSL_PROTOCOL)
        self.timeout = kwargs.get('timeout', DEFAULT_SOCKET_TIMEOUT)
        self.buffer_size = kwargs.get('buffer_size', DEFAULT_BUFFER_SIZE)

    def __enter__(self):
        self.base_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.base_sock.settimeout(self.timeout)

        if self.secure:
            ssl_context = ssl.SSLContext(self.protocol)
            self.ssl_sock = ssl_context.wrap_socket(self.base_sock)
            self.sock = self.ssl_sock
        else:
            self.sock = self.base_sock
        
        self.Connect()
        return self

    def __exit__(self, type, value, traceback):
        if traceback:
            print_exception(type, value, traceback)
        self.Disconnect()
        return True

    def Connect(self):
        try:
            self.sock.connect(self.addr)
        except ssl.SSLError:
            traceback.print_exc()
        except socket.timeout:
            traceback.print_exc()

    def Disconnect(self):
        try:
            self.sock.close()
        except:
            print("Error closing Socket...")

    def Send(self, data):
        if self.secure:
            self.sock.write(data)
        else:
            self.sock.send(data)

    def Receive(self, max_data=None):
        response = ''
        while True:
            data = self.sock.recv(self.buffer_size)
            if not data:
                break
            response += data
        if max_data:
            response = response[:max_data]
        return response

    
