from machine import Pin,ADC
import time
from keras_lite import Model  # 從 keras_lite 模組匯入 Model
import ulab as np             # 匯入 ulab 模組並命名為 np


model = Model('temperature_model.json')     # 建立模型物件

#增加神經網路的參數與模型
mean = 170.98275862068965  #平均值
std = 90.31162360353873    #標準差

adc_pin = Pin(36)        
adc = ADC(adc_pin)       
adc.width(ADC.WIDTH_9BIT)
adc.atten(ADC.ATTN_11DB) 

data=0

while True:            
    for i in range(20):              
        thermal=adc.read()     
        data=data+thermal      
        time.sleep(0.01)
    
    data = data/20    

    print(int(data),end='   ')    # 顯示ADC值;end=''代表不換行        
    
    data = np.array([data])  # 將data轉換成array格式
    data = data-mean              # data減掉平均數
    data = data/std               # data除以標準差
    tem = model.predict(data)     # 得出預測值
    tem = round(tem[0]*100, 1)     # 將預測值×100等於預測溫度
    print(tem)
    
    data = 0
    time.sleep(1)      # 暫停1秒
