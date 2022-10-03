import utime # 匯入 utime 模組用以計時
from machine import Pin, ADC
import network, ESPWebServer


adc_pin = Pin(36)         # 36是ESP32的VP腳位
adc = ADC(adc_pin)        # 設定36為輸入腳位          
adc.width(ADC.WIDTH_9BIT) # 設定分辨率位元數(解析度)
adc.atten(ADC.ATTN_11DB)  # 設定最大電壓

gsr_val = 180             # 膚電反應預設值

def handleCmd(socket, args):    # 處理 /handleCmd 指令的函式
    ESPWebServer.ok(socket, "200", str(gsr_val))

def gsr_converter(raw_val, min_val, max_val):    # 將膚電反應對應到180~360的函式
    raw_val *= -1
    gsr_val = ((raw_val + max_val)
        /(max_val - min_val)*(360 - 180) + 180)
    return gsr_val

print("連接中...")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("FLAG", "0233110330")

while not sta.isconnected():
    pass

print("已連接, ip為:", sta.ifconfig()[0])

ESPWebServer.begin(80)                  # 啟用網站
ESPWebServer.onPath("/lie", handleCmd)  # 指定處理指令的函式

time_mark = utime.ticks_ms()    # 取得當前時間
while True:
    # 持續檢查是否收到新指令
    ESPWebServer.handleClient()
    
    # 當計時器變數與現在的時間差小於 0 則執行任務
    if utime.ticks_diff(utime.ticks_ms(), time_mark) > 100:
        raw_val = adc.read()
        gsr_val = gsr_converter(raw_val, 400, 511)
        time_mark = utime.ticks_ms() # 重置計時器
