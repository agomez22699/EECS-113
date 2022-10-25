#Adrian Gomez
#SID: 20119988
#EECS 113
#Final Project

import Adafruit_DHT
from Adafruit_LCD1602 import Adafruit_CharLCD
from PCF8574 import PCF8574_GPIO
from CIMIS_Extract import *
import RPi.GPIO as GPIO
import time
import threading
import sys

#timers
water_timer_left   = 0  #timer for how long sprinkler should be on
water_timer_start  = 0  #when watering starts

#LCD Setup and Global Variables
PCF8574_address = 0x27
mcp = PCF8574_GPIO(PCF8574_address)
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2,pins_db=[4,5,6,7],GPIO=mcp)
Line1=""

#Local Data Initialization
ET = 0
humidity=0
temperature=0
average_temperature = 0
average_humidity = 0

#Moving GPIO pin numbers into Varaibles
relayPin = [25]
pirPin = 12
dhtType = 11
dhtPin = 4

#CIMIS Object Pointer
cimis = None

# flags
motion = 0
relayActivity = False
dhtActivity = False
Relay_already_on = False

# thread pointers
PIR_thread   = None
DHT_thread   = None
Relay_thread = None

#----------------------------------------------------------- Start of Functions here------------------------------------------------------------#

#connect GPIO pins for sensors
def setup():
    global pirPin
    global dhtPin
    global relayPin
    global cimis
    lcdSetup() #Starting the LCD
    GPIO.setmode(GPIO.BCM)#setting GPIO environment 
    GPIO.setwarnings(False)
    GPIO.setup(dhtPin, GPIO.IN) #dht pin
    GPIO.setup(pirPin, GPIO.IN) #PIR pin
    GPIO.setup(relayPin, GPIO.OUT) #relay pin
    cimis = CIMIS()
    turnOffRelay(True)
#------------------------------------------------------------------------- Dht functions --------------------------------------------------------------------------------
def dht_update():
    while True:
        global humidity
        global temperature
        humidity, temperature = Adafruit_DHT.read_retry(dhtType, dhtPin)
        time.sleep(1)
        
def dht_function():
        global humidity
        global temperature
        global dhtActivity
        global relayActivity
        global average_humidity
        global average_temperature
        global water_timer_left
        global water_timer_start
        global dhtPin
        global dhtType
        
        minutes = 0
        myThread=threading.Thread(target=dht_update)
        myThread.daemon=True
        myThread.start()
        temperature_list    = []
        humidity_list       = []
        list_size=6
        
        
        for i in range(list_size):
            
            temperature_list.append(0)
            humidity_list.append(0)
            
        while True:
                if dhtActivity:
                        print('Temp: ' + str(temperature) + 'C' + '     Humidity: ' + str(humidity))
                        
                        humidity_list[minutes] = humidity
                        temperature_list[minutes] = temperature
                        
                        if minutes == 5:
                                minutes=0
                                average_temperature = calculate_average(temperature_list, len(temperature_list))
                                average_humidity    = calculate_average(humidity_list, len(humidity_list))
                                
                                print("Local Average Temp.: ", average_temperature, "C")
                                print("Local Average Hum.: ", average_humidity, "%")
                                
                                cimis.update_values() #Extract CIMIS data
                                ShowStats() #Show the Data on LCD
                                calculate_ET() #Calculate ET
                                gallons = calculate_irrigation()
                                water_timer_left = float( ( float(gallons) / float(1024) )  * float(3600)) #Display the Watering Time in Seconds
                                
                                print("Water timer left: ", water_timer_left)#display time spent watering
                                if (water_timer_left > 0):
                                        print("Starting Sprinkler Now\n")
                                        
                                        water_timer_start = time.time()
                                        relayActivity = True
                                        dhtActivity = False
                        else:
                            time.sleep(5)#wait
                            minutes += 1 #increment time
                            
#----------------------------------------------------------------------- calculation functions ----------------------------------------------------------------------

def calculate_irrigation(): #calulating data from calling function
    
        global cimis
        PF = 1.0
        return (cimis.ET0 * PF * 200 * 0.62) / 0.75
    
def calculate_ET():
        global cimis
        global CIMIS_humidity
        global average_humidity
        global ET
        
        if(cimis.humidity==0 or average_humidity==0):#doesnt return infinite numbers
            ET=0
            return
        
        ET = float(cimis.ET0) / (float(average_humidity)/float(cimis.humidity))
        print("Local humidity: ", average_humidity)
        print("CIMIS humidity: ", cimis.humidity)
        print("local ET: ", ET)



def calculate_average(list, size): #Function to Calculate Average with a sent List
        sum = 0
        for i in range(size):
            
                sum += list[i]
                
        return float(sum)/float(size) 

#------------------------------------------------- pir fuunction -------------------------------------------------------------------------------------------
        
def pir_function(): 
        global relayActivity
        global pirPin
        global motion
        global water_timer_start
        global water_timer_left
        start_timer = 0
        while True:
                motion = GPIO.input(pirPin)==1
                if (relayActivity and motion ==1):
                    
                        print("\nMotion detected, stopping sprinklers.")
                        relayActivity = False
                        
                        start_PIR_time   =time.time() #starting the PIR timer
                        
                        water_timer_left =water_timer_left - (float(start_PIR_time) - float(water_timer_start))
                        
                        current_time = time.time()
                        
                        time_diff =current_time - start_PIR_time
                        
                        lcdShowMotionDetected() #displays interrupt on LCD

                        while motion == 1 and time_diff < 60: #Keeps Sprinkler off if theres motion, otherwise continue
                                relayActivity = False #stop the function if greater than a minute
                                current_time = time.time()
                                time_diff    = current_time - start_PIR_time
                                motion = GPIO.input(pirPin)
                        relayActivity = True #Resuming tasks when motion is no longer detected
                        water_timer_start = time.time()
                        lcdShowResumeOperation() #Displays that Sprinkers have resumed motion
                        time.sleep(0.5)
#------------------------------------------------- Start of RElay Block -----------------------------------------------------------------------------------------------#

def Relay_func():
        global relayActivity
        global water_timer_left
        global water_timer_start
        global dhtActivity
        global Relay_already_on
        
        Relay_already_on = True
        time_diff = 0
        #lcd.clear()
        while True:
                if relayActivity and time_diff < water_timer_left : #This is thecase where relay is ON and there is watering time left in the variable
                    
                        Relay_already_on = turnOnRelay(Relay_already_on)# Turn on Relay
                        time_diff = float(time.time()) - float(water_timer_start) #Update Watering TIme
                        print("Time passed for sprinklers: ", time_diff)
                        
                elif not relayActivity and water_timer_left > 0: #This is the case where relay is off bc of interrupt from PIR sensor
                    
                        Relay_already_on = turnOffRelay(Relay_already_on)   #turnning off the relay
                        
                elif relayActivity and time_diff >= water_timer_left: #case where timer reaches 0 or slightly below
                    
                        water_timer_left=0 #Resetting Water timer
                        
                        turnOffRelay(Relay_already_on) #turning off the relay
                        
                        dhtActivity = True #Starting DHT
                        
                        Relay_already_on = False
                        
                        relayActivity = False
                        
                        print("Sprinklers are now OFF\n")
                        
                        time.sleep(0.5)
def turnOffRelay(param): #To turn on the relay
        global relayPin,Relay_already_on
        
        if Relay_already_on:
            
                for pin in relayPin:
                    
                        GPIO.output(pin, GPIO.LOW)
                        
                Relay_already_on=False
                return False
        else: 
                return True
            
def turnOnRelay(param): #To turn on the Relay
        global relayPin,Relay_already_on
        
        if not Relay_already_on:
            
                for pin in relayPin:
                    
                        GPIO.output(pin, GPIO.HIGH)
                        
                return True
        else: 
                return False            
          
#-------------------------------------------------------- Start of LCD Block---------------------------------------------------------------------#
def lcdSetup():
    global Line1
    mcp.output(3,1)
    lcd.begin(16,2)
    Line1 = "EECS113 \nFinal Project"
    updateLCD()
    
def updateLCD():
    global Line1
    lcd.clear()
    message = str(Line1)
    lcd.message(message)
    lcd.autoscroll()
    time.sleep(1)
    
def lcdShowMotionDetected():
    global Line1
    Line1="MD!\nSprinkler OFF" #update line 1
    updateLCD()

def lcdShowResumeOperation():
    global Line1
    Line1="Turning\nSprinkler ON" #update line 1
    updateLCD()

def ShowStats():
    global Line1
    Line1=getString()
    updateLCD()

def getString():
        global average_temperature
        global average_humidity
        global cimis
        
        localTemp=str(round(average_temperature,1))
        
        localHumid=str(round(average_humidity,1))
        
        cimisTemp="0" if(cimis==None) else str(round(cimis.temperature,1))
        
        cimisHumid="0" if(cimis==None) else str(round(cimis.humidity,1))
        
        cimisET0="0" if(cimis==None) else str(cimis.ET0)
        
        return "Local Data:T "+localTemp+" C. H "+localHumid+"% ET "+str(round(ET,4))+"\nCIMIS Data:T "+cimisTemp+" C. H "+cimisHumid+"% ET "+cimisET0

#-------------------------END of LCD Block------------------------------------------------------------------------------------------------------------------------------#
def inLoop():
        global dhtActivity
        global DHT_thread
        global Relay_thread
        global PIR_thread
        
        dhtActivity = True
        DHT_thread = threading.Thread(target=dht_function)
        DHT_thread.daemon = True
        DHT_thread.start()
        

        PIR_thread = threading.Thread(target=pir_function)
        PIR_thread.daemon = True
        PIR_thread.start()


        Relay_thread = threading.Thread(target = Relay_func)
        Relay_thread.daemon = True
        Relay_thread.start()

#----------------------- END of inLoop ----------------------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
        setup()
        inLoop()