#!/usr/bin/env python
from useragent import UserAgent, DEFAULT_HEADERS


class HooliHacker:
    def __init__(self, **kwargs):
        self.username = 'littleBobbyTables'
        self.parameters = {'username': self.username}
        self.headers = DEFAULT_HEADERS
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_response_code(self, data):
        try:
            return data.split()[-1].strip('"')
        except:
            return None
    def get_flag(self, data):
        flag = self.get_response_code(data)
        if flag and len(flag) == 56:
            return flag
        return None
    def solve_captcha(self, data):
        function = self.get_response_code(data)
        operations = {
            '+': (lambda a,b: a+b), '-': (lambda a,b: a-b),
            '*': (lambda a,b: a*b), '/': (lambda a,b: a/b),
        }
        for symbol, operation in operations.items():
            if symbol in function:
                a, b = function.split(symbol)
                return str(operation(int(a), int(b)))
    
    def get_token(self):
        ua = UserAgent('POST', self.ip + '/getSecure', 
            parameters=self.parameters, ie_headers=True)
        status_code, headers, message = ua.SendRequest()
        self.parameters['token'] = self.get_response_code(message)

    def lab2_a1(self):
        ua = UserAgent('POST', self.ip + '/', 
            headers=DEFAULT_HEADERS)
        status_code, headers, message = ua.SendRequest()
        return self.get_flag(message)
    
    def lab2_a2(self):
        self.get_token()

        ua = UserAgent('POST', self.ip + '/getFlag2', 
            parameters=self.parameters, ie_headers=True)
        status_code, headers, message = ua.SendRequest()
        return self.get_flag(message)
    def lab2_a3(self):
        self.get_token()
        
        ua = UserAgent('POST', self.ip + '/getFlag3Challenge', 
            parameters=self.parameters, ie_headers=True)
        status_code, headers, message = ua.SendRequest()

        self.parameters['solution'] = self.solve_captcha(message)
        ua = UserAgent('POST', self.ip + '/getFlag3Challenge', 
            parameters=self.parameters, ie_headers=True)
        status_code, headers, message = ua.SendRequest()
        return self.get_flag(message)
    def lab2_a4(self):
        self.get_token()
        
        ua = UserAgent('POST', self.ip + '/createAccount', 
            parameters=self.parameters, headers=self.headers, ie_headers=True)
        status_code, headers, message = ua.SendRequest()

        self.parameters['password'] = self.get_response_code(message)
        ua = UserAgent('POST', self.ip + '/login', 
            parameters=self.parameters, headers=self.headers, ie_headers=True)
        status_code, headers, message = ua.SendRequest()
        return self.get_flag(message)
    

if __name__ == '__main__':
    hh = HooliHacker(ip='54.209.150.110')
    print('Activity 1 Flag: {}'.format(hh.lab2_a1()))
    print('Activity 2 Flag: {}'.format(hh.lab2_a2()))
    print('Activity 3 Flag: {}'.format(hh.lab2_a3()))
    print('Activity 4 Flag: {}'.format(hh.lab2_a4()))


