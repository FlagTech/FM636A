import network, ESPWebServer
from machine import Pin, ADC
from pulse_oximeter import IIR_filter
from utime import ticks_ms, ticks_diff
import utime
import _thread

led = Pin(2, Pin.OUT)

adc_pin = Pin(36)        
adc = ADC(adc_pin)       
adc.width(ADC.WIDTH_10BIT)
adc.atten(ADC.ATTN_11DB) 

thresh_generator = IIR_filter(0.9)

rsp_rate_timer = utime.ticks_ms()

is_breathing = False
breath_time_mark = ticks_ms()
rsp_rate = 0
num_breath = 0
target_n_breath = 2
tot_intval = 0
rsp = 0

def cal_rsp_rate(intval, target_n_breath=2):
    intval /= 1000
    rsp_rate = target_n_breath/(intval/60)
    rsp_rate = round(rsp_rate, 1)
    return rsp_rate

def SendRspRate(socket, args):    # 處理 /sendata 指令的函式
    ESPWebServer.ok(socket, "200", str(rsp_rate))
    
def SendRsp(socket, args):    # 處理 /line 指令的函式
    ESPWebServer.ok(socket, "200", str(rsp_val))
    
def web_thread():    # 處理網頁的子執行緒函式
    while True:
        ESPWebServer.handleClient()

print("連接中...")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("無線網路名稱", "無線網路密碼")

while not sta.isconnected():
    pass

print("已連接, ip為:", sta.ifconfig()[0])

ESPWebServer.begin(80)                  # 啟用網站
ESPWebServer.onPath("/sendata", SendRspRate)  # 指定處理指令的函式
ESPWebServer.onPath("/line", SendRsp)  # 指定處理指令的函式
ESPWebServer.setDocPath("/")   # 指定 HTML 檔路徑

_thread.start_new_thread(web_thread, ())    # 啟動子執行緒

time_mark = ticks_ms()
while True:            
    if utime.ticks_diff(ticks_ms(), time_mark) > 300:
        rsp = adc.read()
        thresh = thresh_generator.step(rsp)
        
        if rsp > (thresh + 3) and not is_breathing:
            is_breathing = True
            led.value(1)
            
            intval = ticks_diff(ticks_ms(), breath_time_mark)
            if 2000 > intval > 270:
                tot_intval += intval
                if num_breath == target_n_breath:
                    rsp_rate = cal_rsp_rate(
                        tot_intval, target_n_breath)
                    print(rsp_rate)
                    tot_intval = 0
                    num_breath = 0
            else:
                tot_intval = 0
                num_breath = 0
            breath_time_mark = ticks_ms()
        elif rsp < thresh:
            is_breathing = False
            led.value(0)
       
        time_mark = ticks_ms() # 重置定時器
