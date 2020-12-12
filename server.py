import cherrypy
import json
import random
import datetime
import string
import urllib.parse
import kasaSimDevice
import kasaSimBulb

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 8080

device = kasaSimBulb.kasaSimBulb(
                'http://' + SOCKET_HOST + ':' + str(SOCKET_PORT),
                "B15013761762C414871EBA887DE3B424E9C6FD4D", # ('%040x' % random.randrange(16**40)).upper()
                "Smart Wi-Fi LED Bulb with Color Changing",
                "1.0",
                "Bulb1",
                "42C7C7F55EB2", # ('%012x' % random.randrange(16**12)).upper()
                "E85DA6B8E44E2709840FE1DC781CA3A9", # ('%032x' % random.randrange(16**32)).upper()
                "LB130(EU)",
                "FC0C56395DFC9C14C3367DC8F4F9EA59" # ('%032x' % random.randrange(16**32)).upper()
                )

devices = list()
devices.append(device)

@cherrypy.expose
class KasaSim(object):
    ERRORS = {
    -10000: {"http_code":400, "msg":"400 returned for /{} with message Bad Request"},
    -10100: {"http_code":200, "msg":"JSON format error"},
    -20103: {"http_code":200, "msg":"The method does not exist or is not available"},
    -20104: {"http_code":200, "msg":"Parameter doesn't exist"},
    -20601: {"http_code":200, "msg":"Incorrect email or password"},
    -20651: {"http_code":200, "msg":"Token expired"}
    }

    METHODS = {
        'login': {
            'params':['appType','cloudPassword','cloudUserName','terminalUUID']
        },
        'getDeviceList': {}
    }

    REGTIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    USERNAME = 'niouf@niouf.fr'
    PASSWORD = 'niorf'
    COUNTRY = 'FR'

    tokens = dict()

    @cherrypy.tools.json_out()
    #@cherrypy.tools.json_in()
    def POST(self, *args, **querystring):
        content_length = int(cherrypy.request.headers['Content-Length'])
        if content_length == 0:
            return self.returnError(-10000,'/'.join(args))
        data = cherrypy.request.body.read()
        try:
            data = json.loads(data)
        except:
            return self.returnError(-10100)
        check_request = self.check_request(data,querystring)
        if check_request['error_code'] != 0:
            return check_request

        if data['method'] == 'login':
            return self.meth_login(data['params'])

        if data['method'] == 'getDeviceList':
            return self.meth_getDeviceList()
        return self.returnError(-10000,'/'.join(args))

    def check_request(self,data,querystring):
        if 'method' not in data:
            return self.returnResponse(-20103)
        if data['method'] not in self.METHODS:
            return self.returnResponse(-20103)
        method_conf = self.METHODS[data['method']]
        if 'params' in method_conf:
            params_conf = method_conf['params']
            if 'params' not in data:
                return self.returnResponse(-20104)
            else:
                for param in params_conf:
                    if param not in data['params']:
                        return self.returnResponse(-20104)
        if 'token' in querystring:
            if querystring['token'] not in self.tokens:
                return self.returnResponse(-20651)
        else:
            if data['method'] != 'login':
                return self.returnResponse(-20651)
        return {"error_code":0}

    def meth_login(self,params):
        if params['cloudUserName'] != self.USERNAME or params['cloudPassword'] != self.PASSWORD:
            return self.returnResponse(-20601)
        accountId = str(random.randrange(1000000,9999999))
        regTime = datetime.datetime.now().strftime(self.REGTIME_FORMAT)
        countryCode = self.COUNTRY
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        token += '-'+ ''.join(random.choices(string.ascii_letters + string.digits, k=23))
        result = {
            "accountId": accountId,
            "regTime": regTime,
            "countryCode": countryCode,
            "email": params['cloudUserName'],
            "token": token
        }
        self.tokens[token] = result
        return self.returnResponse(0,result)

    def meth_getDeviceList(self):
        deviceList = list()
        for device in devices:
            deviceList.append(device.getDeviceList())
        return self.returnResponse(0,{"deviceList":deviceList})


    def returnResponse(self,error_code,result={},args=""):
        if int(error_code) != 0:
            return self.returnError(error_code,args)
        return {"error_code":0, "result":result}

    def returnError(self,error_code,args=""):
        cherrypy.response.status = self.ERRORS[error_code]['http_code']
        return {"error_code":error_code, "msg":self.ERRORS[error_code]['msg'].format(args)}

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    cherrypy.config.update({
        'server.socket_port': SOCKET_PORT,
        'server.socket_host': SOCKET_HOST}
    )
    cherrypy.quickstart(KasaSim(), '/', conf)