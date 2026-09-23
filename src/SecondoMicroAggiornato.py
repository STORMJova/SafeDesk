from microbit import *
import radio

radio.on()
radio.config(group=1)
display.clear()

SOGLIA_TEMP = 30.0

while True:
    messaggio = radio.receive()
    
    if messaggio:
        print(messaggio)
        
        try:
            parti = messaggio.split(",")
            t = int(parti[0])
            d = int(parti[1])
            
            if t > SOGLIA_TEMP or d < 100:
                display.show(Image.NO)
            else:
                display.show(Image.YES)
                
        except Exception:
            pass
            
    sleep(100)


