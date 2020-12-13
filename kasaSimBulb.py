import kasaSimDevice
import random

DEVICE_TYPE = 'IOT.SMARTBULB'
FW_VER = "1.8.11 Build 191113 Rel.105336"
HW_ID = "111E35908497A05512E259BB76801E10"
DEV_STATE = "normal"
IS_FACTORY = False
DISCO_VER = "1.0"
CTRL_PROTOCOLS = {"name":"Linkie","version":"1.0"}
MODES = ['normal','circadian']
MODE = "normal"

class kasaSimBulb(kasaSimDevice.kasaSimDevice):
    IS_DIMMABLE = 0
    IS_COLOR = 0
    IS_VARIABLE_COLOR_TEMP = 0
    COLOR_MIN = 2700
    COLOR_MAX = 2700
    def __init__(self,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel):
        super().__init__(DEVICE_TYPE,FW_VER,appServerurl,deviceId,deviceName,deviceHwVer,alias,deviceMac,oemId,deviceModel,HW_ID)
        self.dev_state = DEV_STATE
        self.is_factory = IS_FACTORY
        self.disco_ver = DISCO_VER
        self.ctrl_protocols = CTRL_PROTOCOLS
        self.is_dimmable = self.IS_DIMMABLE
        self.is_color = self.IS_COLOR
        self.is_variable_color_temp = self.IS_VARIABLE_COLOR_TEMP
        on_off = random.randrange(0,2)
        light_state = self._rand_light_state()
        self._set_light_state(on_off,light_state['mode'],light_state['hue'],light_state['saturation'],light_state['color_temp'],light_state['brightness'])
        self.preferred_state = list()
        for index in range(4):
            light_state = self._rand_light_state()
            self.preferred_state.append({
                "index":index,
                "hue":light_state['hue'],
                "saturation":light_state['saturation'],
                "color_temp":light_state['color_temp'],
                "brightness":light_state['brightness']
            })
        self.active_mode = "none"
        self.heapsize = 292784

    def _rand_light_state(self):
        mode = MODE
        hue = random.randrange(0,361) if self.is_color else 0
        saturation = random.randrange(0,101) if self.is_color else 0
        color_temp = random.randrange(self.COLOR_MIN,self.COLOR_MAX+1) if self.is_variable_color_temp else self.COLOR_MIN
        brightness = random.randrange(0,101) if self.is_dimmable else 100
        return {"mode":mode,"hue":hue,"saturation":saturation,"color_temp":color_temp,"brightness":brightness}

    def _set_light_state(self,on_off,mode=None,hue=None,saturation=None,color_temp=None,brightness=None):
        self.light_state = {
            "on_off": 1,
            "mode" : mode if not mode is None else self.light_state['mode'],
            "hue" : hue if not hue is None else self.light_state['hue'],
            "saturation" : saturation if not saturation is None else self.light_state['saturation'],
            "color_temp" : color_temp if not color_temp is None else self.light_state['color_temp'],
            "brightness" : brightness if not brightness is None else self.light_state['brightness'],
        }
        if on_off == 0:
            self._toogle_light_state()

    def _toogle_light_state(self):
        if self.light_state['on_off'] == 1:
            dft_on_state = dict()
            dft_on_state['mode'] = self.light_state['mode']
            dft_on_state['hue'] = self.light_state['hue']
            dft_on_state['saturation'] = self.light_state['saturation']
            dft_on_state['color_temp'] = self.light_state['color_temp']
            dft_on_state['brightness'] = self.light_state['brightness']
            self.light_state = {"on_off":0,"dft_on_state":dft_on_state}
        else:
            self.light_state = {
                "on_off": 1,
                "mode" : self.light_state['dft_on_state']['mode'],
                "hue" : self.light_state['dft_on_state']['hue'],
                "saturation" : self.light_state['dft_on_state']['saturation'],
                "color_temp" : self.light_state['dft_on_state']['color_temp'],
                "brightness" : self.light_state['dft_on_state']['brightness']
            }


    def get_sysinfo(self,args):
        return {
            "sw_ver"         : self.fwVer,
            "hw_ver"         : self.deviceHwVer,
            "model"          : self.deviceModel,
            "description"    : self.deviceName,
            "alias"          : self.alias,
            "mic_type"       : self.deviceType,
            "dev_state"      : self.dev_state,
            "mic_mac"        : self.deviceMac,
            "deviceId"       : self.deviceId,
            "oemId"          : self.oemId,
            "hwId"           : self.hwId,
            "is_factory"     : self.is_factory,
            "disco_ver"      : self.disco_ver,
            "ctrl_protocols" : self.ctrl_protocols,
            "light_state"    : self.light_state,
            "is_dimmable"    : self.is_dimmable,
            "is_color"       : self.is_color,
            "is_variable_color_temp": self.is_variable_color_temp,
            "preferred_state": self.preferred_state,
            "rssi"           : self.rssi,
            "active_mode"    : self.active_mode,
            "heapsize"       : self.heapsize,
            "err_code"       : 0
        }
