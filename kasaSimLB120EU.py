import kasaSimBulb
import random

DEVICE_NAME = "Smart Wi-Fi LED Bulb with Tunable White Light"
HW_VER = "1.0"
MODEL = 'LB120(EU)'

class kasaSimLB120EU(kasaSimBulb.kasaSimBulb):
    IS_DIMMABLE = 1
    IS_COLOR = 0
    IS_VARIABLE_COLOR_TEMP = 1
    def __init__(self,appServerurl,deviceId,local_ip,alias,deviceMac,oemId):
        super().__init__(appServerurl,deviceId,local_ip,DEVICE_NAME,HW_VER,alias,deviceMac,oemId,MODEL)
