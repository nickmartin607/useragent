#!/usr/bin/env python
import re
from urllib import quote_plus as urlencode

import patterns


DEBUG = False

DEFAULT_CONNECTION_TYPE =   'close'
DEFAULT_CONTENT_TYPE =      'application/x-www-form-urlencoded'

HTTP_RESPONSE_REGEX = re.compile(patterns.http_response, re.DOTALL)


class Request(object):
    def __init__(self, ua):
        self.headers = ua.headers
        self.headers['Host'] = ua.url.host
        self.parameters = ua.parameters


        # Start request data string
        self.request = '{m} {p} {v}\r\n'.format(
            m=ua.method, p=ua.url.path, v=ua.http_version)
        
        # Handle Request POST Parameters
        parameters = ''
        if ua.method == 'POST':
            pairs = []
            for key, value in self.parameters.items():
                pairs.append(urlencode(key) + '=' + urlencode(value))
            parameters = '&'.join(pairs)
            
            # Set required Headers 
            self.set_post_headers(parameters)
            
        # Handle Request Headers
        if self.headers:
            pairs = []
            for key, value in self.headers.items():
                pairs.append('{}: {}'.format(key, value))
            headers = '\r\n'.join(pairs)
            
            # Add headers onto request
            self.request += headers

        # Add double CRlF onto request
        self.request += '\r\n\r\n'
        # Add parameter string onto request, if it exists
        if parameters:
            self.request += parameters
        
        if DEBUG:
            debug_message(self.request)

    def set_post_headers(self, parameters, 
                                connection=DEFAULT_CONNECTION_TYPE, 
                                content=DEFAULT_CONTENT_TYPE):
        self.headers['Connection'] = str(connection)
        self.headers['Content-Type'] = str(content)
        self.headers['Content-Length'] = str(len(parameters))
        

class Response(object):  
    def __init__(self, data):
        if DEBUG:
            debug_message(data)

        response = HTTP_RESPONSE_REGEX.match(data).groupdict()
        self.status = response.get('status')
        self.message = response.get('message')
        self.headers = {}

        headers = response.get('headers') or ''
        for h in headers.strip().split('\r\n'):
            header = h.split(': ', 1)
            self.headers[str(header[0])] = str(header[1])
        
    def is_2xx(self):
        return self.status.startswith('2')
    def is_3xx(self):
        return self.status.startswith('3')
    def is_4xx(self):
        return self.status.startswith('4')
    def is_5xx(self):
        return self.status.startswith('5')

    def handle_3xx(self, ua):
        try:
            ua.url = URL(self.headers.get('Location'))
            return ua.SendRequest()
        except:
            raise Exception('Location header is not set in request')
        return None


def debug_message(message):
    if DEBUG:
        print("#" * 120)
        print(message)
        print("#" * 120)


if __name__ == '__main__':
    pass