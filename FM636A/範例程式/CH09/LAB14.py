from utime import ticks_ms, ticks_diff
from machine import Pin, ADC
import network, ESPWebServer
from keras_lite import Model  # 從 keras_lite 模組匯入 Model
import ulab as np             # 匯入 ulab 模組並命名為 np


model = Model('temperature_model.json')     # 建立模型物件

mean = 170.98275862068965  #平均值
std = 90.31162360353873    #標準差

adc_pin = Pin(36) 
adc = ADC(adc_pin)
adc.width(ADC.WIDTH_9BIT)
adc.atten(ADC.ATTN_11DB)

temp = 0                   # 溫度

def cal_temp(data):
    data = np.array([data])  # 將data轉換成array格式
    data = data - mean       # data減掉平均數
    data = data/std          # data除以標準差

    temp = model.predict(data)    # 得出預測值
    temp = round(temp[0]*100, 1)  # 將預測值×100等於預測溫度
    return temp

def SendTemp(socket, args):    # 處理 /measure 指令的函式
    ESPWebServer.ok(socket, "200", str(temp))

print("連接中...")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("熱點名稱", "熱點密碼")

while not sta.isconnected():
    pass

print("已連接, ip為:", sta.ifconfig()[0])

ESPWebServer.begin(80)                  # 啟用網站
ESPWebServer.onPath("/measure", SendTemp)  # 指定處理指令的函式

time_mark = ticks_ms()    # 取得當前時間
while True: 
    # 持續檢查是否收到新指令
    ESPWebServer.handleClient()

    # 當計時器變數與現在的時間差大於 100 時則執行任務
    if ticks_diff(ticks_ms(), time_mark) > 100:
        data = adc.read()
        temp = cal_temp(data)
        time_mark = ticks_ms() # 重置定時器
