#!/usr/bin/env python
import bs4
import re
import socket
import ssl
from traceback import print_exception
from urllib import quote_plus as urlencode


DEFAULT_TIMEOUT = 5
DEFUALT_BUFFER_SIZE = 2048
DEFAULT_HTTP_VERSION = 'HTTP/1.1'
DEFAULT_CONNECTION_TYPE = 'close'
DEFAULT_CONTENT_TYPE = 'application/x-www-form-urlencoded'

DEFAULT_HEADERS = {
    'Accept': 'en-US,en;q=0.8',
    'Accept-Language': 
        'text/html,application/xhtml+xml,' + \
        'application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'close',
    'Cache-Control': 'no-cache, no-store, max-age=0',
    'Upgrade-Insecure-Requests': '1',
}
IE_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'UA-CPU': 'AMD64',
    'User-Agent': 
        'Mozilla/5.0 (Windows NT 10.0; Win64; ' + \
        'x64; Trident/7.0; rv:11.0) like Gecko',
}

EMAIL_REGEX = re.compile(
    r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+'
)
URL_REGEX = re.compile(
    r'(?:(?P<scheme>[a-zA-Z0-9.\-+]+)\:\/\/)?' + \
    r'(?:{h}|{ip})'.format(
        h=r'(?P<hostname>[a-zA-Z0-9.\-]+\.[a-zA-Z]+)', 
        ip=r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    ) + \
    r'(?:\:(?P<port>\d+))?' + \
    r'(?:(?P<path>\/[^?&#\\]+))?' + \
    r'(?:\?(?P<query>[^?#\\]+))?' + \
    r'(?:\#(?P<fragment>[^?&#]+))?'
)
HTTP_RESPONSE_REGEX = re.compile(
    r'(?P<http_version>[a-zA-Z]+\/[0-2]\.[0-9])\s' + \
    r'(?P<status_code>\d{3})\s' + \
    r'(?P<status_reason>[\w ]+)' + \
    r'\r\n' + \
    r'(?P<headers>(?:[\w=:;.,/\-\\()\<\"> ]+\r\n)*)?' + \
    r'\r\n' + \
    r'(?P<message>.*$)',
    re.DOTALL
)


class UserAgent(object):
    debug = False

    def __init__(self, method, address, *args, **kwargs):
        self.method = method
        self.url = URL(address)

        self.headers = kwargs.get('headers', {})
        self.parameters = kwargs.get('parameters', {})
        self.http_version = kwargs.get('http_version', DEFAULT_HTTP_VERSION)
    
        self.headers['Host'] = self.url.host
        if kwargs.get('ie_headers', False):
            self.headers.update(IE_HEADERS)
        
        if kwargs.get('debug'):
            self.debug = kwargs.get('debug')
    
    def SendRequest(self):
        parameters = ''
        if self.parameters:
            pairs = []
            for key, value in self.parameters.items():
                pairs.append(urlencode(key) + '=' + urlencode(value))
            parameters = '&'.join(pairs)
            self.headers['Connection'] = DEFAULT_CONNECTION_TYPE                
            self.headers['Content-Type'] = DEFAULT_CONTENT_TYPE   
            self.headers['Content-Length'] = str(len(parameters)) 
        
        headers = ''
        if self.headers:
            pairs = []
            for key, value in self.headers.items():
                pairs.append('{}: {}'.format(key, value))
            headers = '\r\n'.join(pairs)

        request = '{} {} {}'.format(
            self.method, self.url.path, self.http_version)
        request += '\r\n'
        request += headers
        request += '\r\n\r\n'
        if parameters:
            request += parameters
        
        response = ''
        with Connection(self.url.addr, secure=self.url.is_secure) as c:
            if self.debug:
                print("#" * 120); print(request); print("#" * 120)
            c.Send(request)
            response = c.Receive()
            if self.debug:
                print("#" * 120); print(response); print("#" * 120)
        return self.ParseResponse(response)
    
    def ParseResponse(self, response):
        response = HTTP_RESPONSE_REGEX.match(response).groupdict()

        status_code = response.get('status_code')
        message = response.get('message')
        headers = response.get('headers').strip().split('\r\n') 
        headers = [h.split(': ', 1) for h in headers]
        headers = {h[0]:h[1] for h in headers}
        
        if status_code.startswith('3'):
            new_address = headers.get('Location')
            if new_address:
                self.url = URL(new_address)
                self.headers['Host'] = self.url.host
                self.SendRequest()
            else:
                return (status_code, headers, message)
        else:        
            return (status_code, headers, message)
        
    def GetSoup(self, parser=None):
        status_code, headers, message = self.SendRequest()
        if message: 
            soup = bs4.BeautifulSoup(message, 'html.parser', from_encoding='iso-8859-1')
            return parser(soup) if parser else soup                   
        else:
            return ''


class URL(object):
    def __init__(self, address):
        self.address = address
        try:
            url = URL_REGEX.match(address).groupdict()
        except AttributeError:
            raise Exception(
                'Address is not properly formatted: {}'.format(address)
            )
        for key, value in url.items():
            setattr(self, key, value)

        # Set ip based on hostname if not included in address
        if not self.ip:
            try:
                self.ip = socket.gethostbyname(self.hostname)
            except socket.gaierror:
                raise Exception('Unable to find IP for: ' + self.hostname)

        # Set Path to '/' if no path was included in address
        if not url.get('path'):
            self.path = '/'
        
        # Set Scheme/Port if not included in address
        if self.port and not self.scheme:
            self.scheme = 'https' if (self.port == 443) else 'http'
        elif self.scheme and not self.port:
            self.port = 443 if (self.scheme == 'https') else 80
        else:
            self.scheme = 'http'
            self.port = 80

    @property
    def host(self):
        return self.hostname or self.ip
    @property
    def base_host(self):
        return '{scheme}://{host}:{port}'.format(
            scheme=self.scheme, host=self.host, port=self.port)
    @property
    def addr(self):
        return (self.ip, self.port)
    @property
    def is_secure(self):
        return ((self.scheme == 'https') or (self.port == 443))


class Connection(object):
    def __init__(self, addr, **kwargs):
        self.addr = addr
        self.secure = kwargs.get('secure', False)
        self.protocol = kwargs.get('protocol', ssl.PROTOCOL_SSLv23)
        self.timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
    
    def __enter__(self):
        self.Connect()
        return self

    def __exit__(self, type, value, traceback):
        if traceback:
            print_exception(type, value, traceback)
        self.Disconnect()
        return True
    
    def Connect(self):
        if self.secure:
            ssl_context = ssl.SSLContext(self.protocol)
            self.ssl_socket = ssl_context.wrap_socket(self.socket)
            try:
                self.ssl_socket.connect(self.addr)
            except ssl.SSLError:
                traceback.print_exc()
        else:
            try:
                self.socket.connect(self.addr)
            except socket.timeout:
                traceback.print_exc()
    
    def Disconnect(self):
        try:
            if self.secure:
                self.ssl_socket.close()
            else:
                self.socket.close()
        except:
            pass

    def Send(self, data):
        if self.secure:
            self.ssl_socket.write(data)
        else:
            self.socket.send(data)

    def Receive(self, buffer_size=DEFUALT_BUFFER_SIZE):
        response = ''
        while True:
            if self.secure:
                data = self.ssl_socket.read()
            else:
                data = self.socket.recv(buffer_size)
            if not data:
                break
            response += data
        return response


if __name__ == '__main__':
    ua = UserAgent('GET', 'http://gccis.rit.edu/', debug=True)    
    ua.SendRequest()