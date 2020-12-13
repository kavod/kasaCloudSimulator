import kasa
import asyncio
import random

class kasaSimDevice(object):
    RSSI_MIN = -90
    RSSI_MAX = -30
    def __init__(self,deviceType,fwVer,appServerurl,deviceId,local_ip,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel,hwId):
        self.deviceType     = deviceType
        self.role           = 0
        self.fwVer          = fwVer
        self.appServerurl   = appServerurl
        self.deviceRegion   = 'eu-west-1'
        self.deviceId       = deviceId
        self.local_ip       = local_ip
        self.deviceName     = deviceName
        self.deviceHwVer    = deviceHwVer
        self.alias          = alias
        self.deviceMac      = deviceMac
        self.oemId          = oemId
        self.deviceModel    = deviceModel
        self.hwId           = hwId
        self.fwId           = "00000000000000000000000000000000"
        self.isSameRegion   = True
        self.status         = 1
        self.rssi           = random.randrange(self.RSSI_MIN,self.RSSI_MAX)

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
