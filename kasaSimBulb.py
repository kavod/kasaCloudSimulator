import kasaSimDevice

DEVICE_TYPE = 'IOT.SMARTBULB'
FW_VER = "1.8.11 Build 191113 Rel.105336"

class kasaSimBulb(kasaSimDevice.kasaSimDevice):
    def __init__(self,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel,hwId):
        super().__init__(DEVICE_TYPE,FW_VER,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel,hwId)
