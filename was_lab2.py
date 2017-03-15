#!/usr/bin/env python
from useragent import UserAgent, DEFAULT_HEADERS


def read_response(response):
    return response.message.split()[-1].strip('"')
    
def solve_captcha(response):
    function = read_response(response)
    operations = {
        '+': (lambda a,b: a+b), '-': (lambda a,b: a-b),
        '*': (lambda a,b: a*b), '/': (lambda a,b: a/b),
    }
    for symbol, operation in operations.items():
        if symbol in function:
            a, b = function.split(symbol)
            return str(operation(int(a), int(b)))

def get_token(ip):
    ua = UserAgent('POST', '{}/getSecure'.format(ip))
    r = ua.SendRequest()
    return read_response(r)


if __name__ == '__main__':
    ip = '54.209.150.110'
    headers = DEFAULT_HEADERS
    parameters = {
        'username': 'littleBobbyTables',
        'token': get_token(ip),
    }

    # Activity #1
    ua = UserAgent('POST', '{}/'.format(ip))
    r = ua.SendRequest()
    f = read_response(r)
    print('Activity 1 Flag: ' + f)

    # Activity #2
    ua = UserAgent('POST', '{}/getFlag2'.format(ip), 
        parameters=parameters, ie_headers=True)
    r = ua.SendRequest()
    f = read_response(r)
    print('Activity 2 Flag: ' + f)

    # Activity #3
    ua = UserAgent('POST', '{}/getFlag3Challenge'.format(ip), 
        parameters=parameters, ie_headers=True)
    r = ua.SendRequest()
    ua.parameters['solution'] = solve_captcha(r)
    r = ua.SendRequest()
    f = read_response(r)
    print('Activity 3 Flag: ' + f)

    # Activity #4
    ua = UserAgent('POST', '{}/createAccount'.format(ip), 
        parameters=parameters, headers=headers, ie_headers=True)
    r = ua.SendRequest()
    parameters['password'] = read_response(r)
    ua = UserAgent('POST', '{}/login'.format(ip), 
        parameters=parameters, headers=headers, ie_headers=True)
    r = ua.SendRequest()
    f = read_response(r)
    print('Activity 4 Flag: ' + f)



