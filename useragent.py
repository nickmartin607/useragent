#!/usr/bin/env python
import bs4, re
from traceback import print_exception

from util import connection, http, url


DEBUG = False

DEFAULT_HTTP_VERSION =      'HTTP/1.1'
IE_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'UA-CPU': 'AMD64',
    'User-Agent': 
        'Mozilla/5.0 (Windows NT 10.0; Win64; ' + \
        'x64; Trident/7.0; rv:11.0) like Gecko',
}


class UserAgent(object):
    def __init__(self, method, address, *args, **kwargs):
        self.method = method
        self.url = url.URL(address)

        self.headers = kwargs.get('headers', {})
        self.parameters = kwargs.get('parameters', {})
        self.http_version = kwargs.get('http_version', DEFAULT_HTTP_VERSION)
    
        self.headers['Host'] = self.url.host
        if kwargs.get('ie_headers', False):
            self.headers.update(IE_HEADERS)
        
    def SendRequest(self):
        with connection.Connection(self.url.addr, secure=self.url.is_secure) as c:
            request = http.Request(self)
            c.Send(request.request)
            data = c.Receive()
            response = http.Response(data)

            if response.is_3xx():
                return response.handle_3xx(ua)
            
            return response
        
    # def GetSoup(self, parser=None):
    #     response = self.SendRequest()
    #     if message: 
    #         soup = bs4.BeautifulSoup(message, 'html.parser', from_encoding='iso-8859-1')
    #         return parser(soup) if parser else soup                   
    #     else:
    #         return ''


if __name__ == '__main__':
    pass