import kasa
import asyncio
import cherrypy
import json
import random
import datetime
import string
import urllib.parse
import kasaSimDevice
import kasaSimBulb
import kasaSimPlug
import kasaSimLB120EU

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 8080

url = 'http://' + SOCKET_HOST + ':' + str(SOCKET_PORT)

devices = list()
devices.append(kasaSimBulb.kasaSimBulb(
                url,
                "B15013761762C414871EBA887DE3B424E9C6FD4D", # ('%040x' % random.randrange(16**40)).upper()
                "192.168.0.31",
                "Smart Wi-Fi LED Bulb with Color Changing",
                "1.0",
                "Bulb1",
                "42C7C7F55EB2", # ('%012x' % random.randrange(16**12)).upper()
                "E85DA6B8E44E2709840FE1DC781CA3A9", # ('%032x' % random.randrange(16**32)).upper()
                "LB130(EU)"
                ))
devices.append(kasaSimPlug.kasaSimPlug(
                url,
                "F7696A0ED3748B4DA30A1A33C2E9F6ADF973A2B2", # ('%040x' % random.randrange(16**40)).upper()
                "192.168.0.54",
                "Smart Wi-Fi Plug With Energy Monitoring",
                "2.0",
                "Plug1",
                "B88CD4B81A27", # ('%012x' % random.randrange(16**12)).upper()
                "406AB3CCA8E15675A1512CDAB2C7FD66", # ('%032x' % random.randrange(16**32)).upper()
                "HS110(EU)"
                ))
devices.append(kasaSimLB120EU.kasaSimLB120EU(
                url,
                "95C6670C9A39613CCAA9B7F7C9BD12EFE8DD53C9", # ('%040x' % random.randrange(16**40)).upper()
                "192.168.0.21",
                "Bulb1",
                "B7056B4F2085", # ('%012x' % random.randrange(16**12)).upper()
                "F9390828D7591FBCD03DA8FFB60AF5B8" # ('%032x' % random.randrange(16**32)).upper()
                ))

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
    -20651: {"http_code":200, "msg":"Token expired"}
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

    MODULES = {
        'system': ['get_sysinfo']
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

    def meth_passthrough(self,deviceId,requestData):
        device = None
        for dev in devices:
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
        # for module, members in requestData_dict.items():
        #     if module not in self.MODULES:
        #         responseData[module] = {"err_code":-1,"err_msg":"module not support"}
        #     else:
        #         responseData[module] = dict()
        #         for member, values in members.items():
        #             if member not in self.MODULES[module]:
        #                 responseData[module][member] = {"err_code":-2,"err_msg":"member not support"}
        #             else:
        #                 responseData[module][member] = getattr(device, member)(values)
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
    cherrypy.quickstart(KasaSim(), '/', conf)
