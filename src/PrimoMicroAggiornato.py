from microbit import *
import radio
import machine
import utime 

LCD_ADDR = 0x27 

def lcd_write(val, rs):
    high = (val & 0xF0) | rs | 0x08
    low = ((val << 4) & 0xF0) | rs | 0x08
    i2c.write(LCD_ADDR, bytes([high | 0x04, high, low | 0x04, low]))

def lcd_init():
    i2c.init(freq=100000, sda=pin20, scl=pin19)
    sleep(100)
    for cmd in (0x33, 0x32, 0x28, 0x0C, 0x06, 0x01):
        lcd_write(cmd, 0)
        sleep(5)

def lcd_text(testo, riga):
    lcd_write(0x80 if riga == 1 else 0xC0, 0)
    testo = testo + " " * (16 - len(testo))
    for char in testo[:16]:
        lcd_write(ord(char), 1)

radio.on()
radio.config(group=1)

SOGLIA_TEMP = 30.0

try:
    lcd_init()
    lcd_text("Postazione Tx", 1)
    sleep(1000)
except Exception:
    pass 

def misura_distanza():
    pin1.write_digital(0)
    utime.sleep_ms(2) 
    
    pin1.write_digital(1)
    utime.sleep_us(10)
    pin1.write_digital(0)
    
    timeout_start = utime.ticks_us()
    
    while pin2.read_digital() == 0:
        if utime.ticks_diff(utime.ticks_us(), timeout_start) > 30000: 
            return 999.0 
            
    inizio_eco = utime.ticks_us()
    
    while pin2.read_digital() == 1:
        if utime.ticks_diff(utime.ticks_us(), inizio_eco) > 30000: 
            return 999.0
            
    fine_eco = utime.ticks_us()
    
    durata = utime.ticks_diff(fine_eco, inizio_eco)
    return (durata / 2) / 29.1

def misura_temperatura():
    lettura = pin0.read_analog()
    millivolt = lettura * (3300.0 / 1023.0)
    return millivolt / 10.0

# --- 3. CICLO PRINCIPALE ---
while True:
    t = misura_temperatura()
    d = misura_distanza()
    
    try:
        if t > SOGLIA_TEMP:
            lcd_text("PERICOLO:", 1)
            lcd_text("Temp Alta! " + str(int(t)) + "C", 2)
        elif d < 100.0:
            lcd_text("PERICOLO:", 1)
            lcd_text("Distanza < 1m!", 2)
        else:
            lcd_text("Stato: SICURO", 1)
            lcd_text("T:" + str(int(t)) + "C D:" + str(int(d)) + "cm", 2)
    except Exception:
        pass
        
    pacchetto = str(int(t)) + "," + str(int(d))
    radio.send(pacchetto)
        
    sleep(1000)