import time
from machine import SoftI2C, Pin, I2C
from max30102 import MAX30102, MAX30102_PULSE_AMP_MEDIUM
from utime import ticks_ms, ticks_diff
from pulse_oximeter import Pulse_oximeter, IIR_filter

led = Pin(2, Pin.OUT)

my_SCL_pin = 25         # I2C SCL pin number here!
my_SDA_pin = 26         # I2C SDA pin number here!
my_i2c_freq = 400000    # I2C frequency (Hz) here!

i2c = SoftI2C(sda=Pin(my_SDA_pin),
              scl=Pin(my_SCL_pin),
              freq=my_i2c_freq)

sensor = MAX30102(i2c=i2c)
sensor.setup_sensor()
sensor.set_active_leds_amplitude(MAX30102_PULSE_AMP_MEDIUM)

pox = Pulse_oximeter(sensor)
thresh_generator = IIR_filter(0.9)
   

is_beating = False
beat_time_mark = ticks_ms()
hr_rate = 0
num_beats = 0
tot_intval = 0


def cal_hr_rate(intval, target_n_beats=3):
    intval /= 1000
    hr_rate = target_n_beats/(intval/60)
    hr_rate = round(hr_rate, 1)
    return hr_rate

def trim(data, length=200):
    if len(data) > 200:
        data = data[:length]
    else:
        data = data + [0 for _ in range(200 - len(data))]
    return data

data = []
file_hb = open('other.txt','w')    # 開啟txt檔
num_completed = 0

while (True):
    pox.update()
    
    if pox.available():
        red_val = pox.get_raw_red()
        data.append(red_val)
        
        thresh = thresh_generator.step(red_val)
        
        if red_val < (thresh - 20) and not is_beating:
            is_beating = True
            led.value(1)
            
            rr_intval = ticks_diff(ticks_ms(), beat_time_mark)
            if 2000 > rr_intval > 270:
                tot_intval += rr_intval
                num_beats += 1
                if num_beats == 3:
                    hr_rate = cal_hr_rate(tot_intval)
                    data = trim(data)
                    for point in data:
                        print(point)
                    print(hr_rate)
                    yn = input("save or not(Y/N)?")
                    if yn == "y" or yn == "Y":
                        num_completed += 1
                        print("progress rate: %s/10" % (num_completed))
                        file_hb.write(str(data)[1: -1])  # data存到檔案中
                        file_hb.write("\n")             # 換行字元
                        if num_completed == 50:
                            break
                            print("completed!")
                    tot_intval = 0
                    num_beats = 0
                    data = []
            else:
                tot_intval = 0
                num_beats = 0
                data = []
            beat_time_mark = ticks_ms()
        elif red_val > thresh:
            is_beating = False
            led.value(0)

file_hb.close()       