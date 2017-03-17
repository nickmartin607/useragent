#!/usr/bin/env python


# Email Patterns
email =         r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+'


# URL Patterns
scheme =        r'(?P<scheme>[a-zA-Z0-9.\-+]+)\:\/\/'
hostname =      r'(?P<hostname>[a-zA-Z0-9.\-]+\.[a-zA-Z]+)'
ip =            r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
port =          r'(?P<port>\d+)'
path =          r'(?P<path>\/[^?&#\\]+)'
query =         r'(?P<query>[^?#\\]+)'
fragment =      r'(?P<fragment>[^?&#]+)'
# URL Pattern Compositions
host =          r'(?:{h}|{i})'.format(h=hostname, i=ip)
netloc =        r'{h}(?:\:{p})?'.format(h=host, p=port)
url =           r'(?:{s})?{n}(?:{p})?(?:\?{q})?(?:\#{f})?'.format(
    s=scheme, n=netloc, p=path, q=query, f=fragment)


# HTTP Response Patterns
http_version =  r'(?P<http_version>[a-zA-Z]+\/[0-2]\.[0-9])'
status_code =   r'(?P<status>\d{3})'
status_reason = r'(?P<status_reason>[\w ]+)'
headers =       r'(?P<headers>(?:[\w=:;.,/\-\\()\<\"> ]+\r\n)*)?'
message =       r'(?P<message>.*$)'
# HTTP Response Pattern Compositions
http_response_status_line = r'{v}\s{sc}\s{sr}'.format(
    v=http_version, sc=status_code, sr=status_reason)
http_response = r'{sl}\r\n(?:{h})?\r\n(?:{m})?'.format(
    sl=http_response_status_line, h=headers, m=message)


if __name__ == '__main__':
    pass