import kasa
import asyncio
import random
import json

class kasaSimDevice(object):
    RSSI_MIN = -90
    RSSI_MAX = -30
    SYSINFO_REQ = "{\"system\":{\"get_sysinfo\":{}}}"
    def __init__(self,local_ip,appServerurl):
        dev =asyncio.run(kasa.Discover.discover(target=local_ip))[local_ip]
        # sysinfo = asyncio.run(kasa.TPLinkSmartHomeProtocol.query(local_ip,self.SYSINFO_REQ))
        sysinfo_json = dev.sys_info
        print(sysinfo_json)
        if 'mic_type' in sysinfo_json.keys():
            self.deviceType     = sysinfo_json['mic_type']
        elif 'type' in sysinfo_json.keys():
            self.deviceType     = sysinfo_json['type']
        else:
            self.deviceType     = ''
        self.role           = 0
        self.fwVer          = sysinfo_json['sw_ver']
        self.appServerurl   = appServerurl
        self.deviceRegion   = 'eu-west-1'
        self.deviceId       = sysinfo_json['deviceId']
        self.local_ip       = local_ip
        if 'description' in sysinfo_json.keys():
            self.deviceName     = sysinfo_json['description']
        elif 'dev_name' in sysinfo_json.keys():
            self.deviceName     = sysinfo_json['dev_name']
        else:
            self.deviceName     = ''
        self.deviceHwVer    = sysinfo_json['hw_ver']
        self.alias          = sysinfo_json['alias']
        if 'mac' in sysinfo_json.keys():
            self.deviceMac      = sysinfo_json['mac'].replace(':','')
        elif 'mic_mac' in sysinfo_json.keys():
            self.deviceMac      = sysinfo_json['mic_mac'].replace(':','')
        else:
            self.deviceMac      = ''
        self.oemId          = sysinfo_json['oemId']
        self.deviceModel    = sysinfo_json['model']
        self.hwId           = sysinfo_json['hwId']
        self.fwId           = "00000000000000000000000000000000"
        self.isSameRegion   = True
        self.status         = 1
        self.rssi           = sysinfo_json['rssi']


    def passthrough(self,req):
        return asyncio.run(kasa.TPLinkSmartHomeProtocol.query(self.local_ip,req))

    def getDeviceList(self):
        return {
            "deviceType"     : self.deviceType,
            "role"           : self.role,
            "fwVer"          : self.fwVer,
            "appServerurl"   : self.appServerurl,
            "deviceRegion"   : self.deviceRegion,
            "deviceId"       : self.deviceId,
            "deviceName"     : self.deviceName,
            "deviceHwVer"    : self.deviceHwVer,
            "alias"          : self.alias,
            "deviceMac"      : self.deviceMac,
            "oemId"          : self.oemId,
            "deviceModel"    : self.deviceModel,
            "hwId"           : self.hwId,
            "fwId"           : self.fwId,
            "isSameRegion"   : self.isSameRegion,
            "status"         : self.status
        }
