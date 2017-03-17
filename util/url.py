#!/usr/bin/env python
import re, socket

import patterns


HTTP, HTTPS = 'http', 'https'
HTTP_PORT, HTTPS_PORT = 80, 443
ROOT_PATH = '/'

URL_REGEX = re.compile(patterns.url)


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
        self.host = self.hostname or self.ip

        # Set Path to '/' if no path was included in address
        if not url.get('path'):
            self.path = ROOT_PATH
        
        # Set Scheme/Port if not included in address
        if self.port and not self.scheme:
            self.scheme = HTTPS if (self.port == HTTPS_PORT) else HTTP
        elif self.scheme and not self.port:
            self.port = HTTPS_PORT if (self.scheme == HTTPS) else HTTP_PORT
        else:
            self.scheme = HTTP
            self.port = HTTP_PORT

    @property
    def is_secure(self):
        return ((self.scheme == HTTPS) or (self.port == HTTPS_PORT))
    @property
    def addr(self):
        return (self.ip, self.port)
    @property
    def netloc(self):
        return '{h}:{p}'.format(h=self.host, p=self.port)
    @property
    def base_host(self):
        return '{s}://{nl}'.format(s=self.scheme, nl=self.netloc)
    @property
    def full_path(self):
        return self.base_host + self.path


if __name__ == '__main__':
    url = URL('https://www.rit.edu/')
    print(url.netloc)
    print(url.base_host)
    print(url.full_path)
