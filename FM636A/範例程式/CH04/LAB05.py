from machine import SoftI2C, Pin
from max30102 import MAX30102
from utime import ticks_ms, ticks_diff
from pulse_oximeter import Pulse_oximeter
import network, ESPWebServer


my_SCL_pin = 25         # I2C SCL 腳位
my_SDA_pin = 26         # I2C SDA 腳位

i2c = SoftI2C(sda=Pin(my_SDA_pin),
              scl=Pin(my_SCL_pin))

sensor = MAX30102(i2c=i2c)
sensor.setup_sensor()

pox = Pulse_oximeter(sensor) # 使用血氧濃度計算類別

spo2 = 0

def handleCmd(socket, args):    # 處理 /handleCmd 指令的函式
    ESPWebServer.ok(socket, "200", str(spo2))

print("連接中...")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("FLAG", "0233110330")

while not sta.isconnected():
    pass

print("已連接, ip為:", sta.ifconfig()[0])
    
ESPWebServer.begin(80)                  # 啟用網站
ESPWebServer.onPath("/measure", handleCmd)  # 指定處理指令的函式
ESPWebServer.setDocPath("/")   # 指定 HTML 檔路徑

while (True):
    ESPWebServer.handleClient()
    
    pox.update()
 
    spo2 = pox.get_spo2()
    
    if spo2 > 0:
        print("SpO2:", spo2, "%")
