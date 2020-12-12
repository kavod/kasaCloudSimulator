import kasaSimDevice

DEVICE_TYPE = 'IOT.SMARTPLUGSWITCH'
FW_VER = "1.5.4 Build 180815 Rel.121440"
HW_ID = "044A516EE63C875F9458DA25C2CCC5A0"

class kasaSimPlug(kasaSimDevice.kasaSimDevice):
    def __init__(self,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel):
        super().__init__(DEVICE_TYPE,FW_VER,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel,HW_ID)
