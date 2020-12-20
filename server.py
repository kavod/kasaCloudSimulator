import kasa
import asyncio
import cherrypy
import json
import random
import datetime
import string
from operator import itemgetter, attrgetter
import kasaSimDevice

USERNAME = 'niouf@niouf.fr'
PASSWORD = 'niorf'
COUNTRY = 'FR'

ACCOUNTS = [
    {
        "accountId": str(random.randrange(1000000,9999999)),
        "email": USERNAME,
        "password": PASSWORD,
        "country": COUNTRY,
        "regTime": datetime.datetime.now(),
        "uuid": ''
    }
]

SOCKET_HOST = '192.168.0.7'
SOCKET_PORT = 8080

url = 'http://' + SOCKET_HOST + ':' + str(SOCKET_PORT)

devices = list()
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.205",url)) # HS300
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.200",url))
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.201",url))
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.202",url)) # HS110(US)
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.209",url)) # HS110(EU)
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.203",url)) # HS200(EU)
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.204",url)) # HS220(EU)
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.206",url)) # LB100
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.207",url)) # LB120
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.208",url)) # LB130
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.210",url)) # HS103
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.21",url)) # LB120
devices.append(kasaSimDevice.kasaSimDevice("192.168.0.31",url)) # LB130

@cherrypy.expose
class KasaSim(object):
    ERRORS = {
    -1    : {"http_code":200, "msg":"module not supported"},
    -2    : {"http_code":200, "msg":"member not supported"},
    -10000: {"http_code":400, "msg":"400 returned for /{} with message Bad Request"},
    -10100: {"http_code":200, "msg":"JSON format error"},
    -20103: {"http_code":200, "msg":"The method does not exist or is not available"},
    -20104: {"http_code":200, "msg":"Parameter doesn't exist"},
    -20580: {"http_code":200, "msg":"Account is not binded to the device"},
    -20601: {"http_code":200, "msg":"Incorrect email or password"},
    -20651: {"http_code":200, "msg":"Token expired"},
    -20675: {"http_code":200, "msg": "Account login in other places"}
    }

    METHODS = {
        'login': {
            'params':['appType','cloudPassword','cloudUserName','terminalUUID']
        },
        'getDeviceList': {},
        'passthrough': {
            'params':['deviceId',"requestData"]
        }
    }

    REGTIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    MAX_SESSIONS = 20

    accounts = list()
    devices = list()
    tokens = dict()

    def __init__(self,accounts,devices):
        self.accounts = accounts
        self.devices = devices

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

        if data['method'] == 'passthrough':
            return self.meth_passthrough(data['params']['deviceId'],data['params']['requestData'])
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
            if self.tokens[querystring['token']]['erased']:
                return self.returnResponse(-20675)
        else:
            if data['method'] != 'login':
                return self.returnResponse(-20651)
        return {"error_code":0}

    def meth_login(self,params):
        account = [acc for acc in self.accounts if acc['email'] == params['cloudUserName'] and acc['password'] == params['cloudPassword']]
        if len(account)<1:
            return self.returnResponse(-20601)
        account = account[0]
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        token += '-'+ ''.join(random.choices(string.ascii_letters + string.digits, k=23))
        self.tokens[token] = {
            "accountId": account['accountId'],
            "time": datetime.datetime.now(),
            "erased": False
        }
        to_be_erased = [tok for tok in self.tokens.values() if tok['accountId'] == account['accountId'] and not tok['erased']]
        # print(to_be_erased)
        to_be_erased = sorted(to_be_erased, key=lambda i:i['time'],reverse=True)
        to_be_erased = sorted(to_be_erased, key=lambda i:i['accountId'])
        # print(to_be_erased[self.MAX_SESSIONS:])
        for d in to_be_erased[self.MAX_SESSIONS:]:
            d['erased'] = True
        # print(self.tokens)
        result = {
            "accountId": account['accountId'],
            "regTime": account['regTime'].strftime(REGTIME_FORMAT),
            "countryCode": account['country'],
            "email": account['email'],
            "token": token
        }
        return self.returnResponse(0,result)

    def meth_getDeviceList(self):
        deviceList = list()
        for device in self.devices:
            deviceList.append(device.getDeviceList())
        return self.returnResponse(0,{"deviceList":deviceList})

    def meth_passthrough(self,deviceId,requestData):
        device = None
        for dev in self.devices:
            if dev.deviceId == deviceId:
                device = dev
        if device is None:
            return self.returnError(-20580)

        responseData = dict()
        try:
            requestData_dict = json.loads(requestData)
        except:
            return self.returnError(-10100)
        responseData = device.passthrough(requestData)
        return self.returnResponse(0,{"responseData":json.dumps(responseData,separators=(',', ':'))})


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
    cherrypy.quickstart(KasaSim(ACCOUNTS,devices), '/', conf)
