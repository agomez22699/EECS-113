#Adrian Gomez
#20119988
#Assignment 4
#05/25/2020

#----------- Importing Libs ----------------------#
import threading 
from time import sleep
import RPi.GPIO as GPIO
#-------------------------------------------------#

#-------------- Setup ----------------------------#
GPIO.setmode(GPIO.BCM) #Setting up GPIO pins
GPIO.setwarnings(False) #Turning off Warnings
#-------------------------------------------------#

#--------------- GPIO Setup ----------------------#
#Buttons
bButton = 22 #Setting up GPIO port 22 as bButton
yButton = 27 #Setting up GPIO port 27 as yButton
rButton = 18 #Settinh up GPIO port 18 as rButton
gButton = 25 #Setting up GPIO port 25 as gButton

#LEDs
gLED = 5 #Setting up GPIO port 5 as gLED
rLED = 6 #Setting up GPIO port 6 as rLED
yLED = 12 #Setting up GPIO port 12 as yLED
bLED = 13 #Setting up GPIO port 13 as bLED

#------------------ Variables ---------------------#
Max_Time = 7 #timer is going to be 7 seconds

blinking_thread = None

#----------------------- Registering Buttons ------------------#
GPIO.setup(bButton,GPIO.IN,pull_up_down=GPIO.PUD_UP) #Buttons are inputs
GPIO.setup(yButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(rButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(gButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
#---------------------------------------------------------------#

#----------------------- Registering LEDs --- ------------------#
GPIO.setup(bLED,GPIO.OUT) #LEDs are ouputs 
GPIO.setup(yLED,GPIO.OUT)
GPIO.setup(rLED,GPIO.OUT)
GPIO.setup(gLED,GPIO.OUT)
#---------------------------------------------------------------#

#----------------- Initiating Variables for Functions ----------#
y_stats = 0
b_stats = 0
blinking_stats = 0 #initated to be off
#-------------------------- Initiating LEDs to off -------------#
GPIO.output(bLED,0)
GPIO.output(yLED,0)
GPIO.output(rLED,0)
GPIO.output(gLED,0)
#---------------------------------------------------------------#

#--------------------------------------- Function for Blue and Yellow Blinking Modes -------------------------------------------#
def blue_blinkEnable(buttonPressed):
    global blinking_stats
    global bButton
    global yButton
    global y_stats
    global b_stats
  
    if(y_stats == 0 and blinking_stats == 0):
        print("Blue Button set Blinking Mode ON")
        GPIO.output(bLED,1) #turning on blue led
        GPIO.output(yLED,0) #turning off yellow led
        sleep(1)
        b_stats = 1 #setting blue stats to 1
        blinking_stats = 0
        
    elif(y_stats == 1 and blinking_stats == 0): #checks if y_status is 1 and blinking_stats = 0
        print("Blue Blinking Mode was stopped due to the Timer")
        GPIO.output(yLED,0) #turning off Yellow LED
        y_stats = 0 #resetting ywllow status
        #checks to see if yellow_status is 0 and blink_status is 0      
  
    elif(y_stats == 1 and blinking_stats == 1): #checks if yellow is on and if blinking status is on
        print("Blue Blinking Mode was stopped by Yellow Button")
        GPIO.output(bLED,0) #turning off Blue LED
        GPIO.output(yLED,0) #turning off Yellow LED
        sleep(1)
        blinking_stats = 0 #resetting blinking_stats
        b_stats = 0 #resetting blue status
        y_stats = 0 #resetting yellow status          
        
def yellow_blinkEnable(buttonPressed):
    #gloabal variables for function
    global yButton
    global bButton
    global blinking_stats
    global y_stats
    global b_stats
    
    if(b_stats == 0 and blinking_stats == 0): #checks to see if blue_status is off and blink_status is off
        print("Yellow Button set Blinking Mode ON")
        GPIO.output(yLED,1) #turning on Yellow LED
        GPIO.output(bLED,0) #Turning off Blue LED
        sleep(1) 
        y_stats = 1 #to enable yellow blinking mode
        blinking_stats = 0
    elif(b_stats == 1 and blinking_stats == 0): #checks if b_stats is on and if blinking is off
        print("Yellow Blinking Mode was stopped due to the Timer")
        GPIO.output(bLED,0) #turning off Blue LED
        b_stats = 0 #resetting Blue Status
    
    elif(blinking_stats == 1 and b_stats == 1): #checks if blue is on and if blinking is on
        print("Yellow Blinking Mode was stopped by the Blue Button") 
        GPIO.output(yLED,0) #turning off Yellow LED
        GPIO.output(bLED,0) #turning off Blue LED
        sleep(1)
        blinking_stats = 0 #resetting blinking_stats
        b_stats = 0 #resetting blue status
        y_stats = 0 #resetting yellow status
        
 #---------------------------------------------------------------------------------------------------------------------------#
# ------------------------ Red and Green Button Function -----------------------------------------#
def redandgreen_button(rgbutton): #Function for Red & Green LEDs and buttons
    global bButton
    global yButton
    global y_stats
    global b_stats
    global blinking_stats
    global blink_thread
    
    print("Red and Green LEDs are Blinking")
    
    if(GPIO.input(gButton) == 1 and blinking_stats == 1 and GPIO.input(rButton) == 1):
            timer_thread() #calling timer
            redandgreen_blinking_thread() #calling blink for red and green
    blinking_stats = 1
 #--------------------------------------------------------------------------------------------------#
#------------------------------- Timer Functions ---------------------------------------------------#
def timer(): #LED Timeout
    global blinking_stats
    
    sleep(Max_Time) #Sleeps for the max time (7seconds)
    Timing_Capacity = Max_Time # Transferring Value
    
    while(Timing_Capacity > 0 and blinking_stats == 1):
        sleep(1)
        Timing_Capacity -= 1 #Decreasing by 1 second
    if(blinking_stats == 1):
        GPIO.output(rLED,0) # Turning off Red LED
        GPIO.output(gLED,0) # Turning off Green LED
        blinking_stats = 0

#------------------------------ Blinking LEDs ------------------------------------------------------#
def Blinking_LED(): #for blinking the Red and Green LEDs
    global gLED
    global rLED
    global blinking_stats
    
    while (True):
         if(blinking_stats == 1):
             #Turning On the LEDs
            GPIO.output(rLED,1) # Turning Red LED ON
            GPIO.output(gLED,1) # Turning Green LED ON
            
            #Sleeping
            sleep(1)
            
            #Turning LEDs Off
            GPIO.output(rLED,0) #Turning Red LED OFF
            GPIO.output(gLED,0) # Turning Green LED OFF
            
            sleep(1)
            
         else:
             #Otherwise, turn off the LEDs
             GPIO.output(rLED,0)
             GPIO.output(gLED,0) 
 #---------------------------- Threading ---------------------------#
def redandgreen_blinking_thread():
    blink_thread = threading.Thread(target = Blinking_LED)   
    blink_thread.daemon = True
    blink_thread.start()
    
def timer_thread():
    time_thread = threading.Thread(target = timer)
    time_thread.daemon = True
    time_thread.start()
    
#------------------------------ Interrupt-----------------------------------------------------------------------------------------------#
def Interrupt():
    GPIO.add_event_detect(bButton, GPIO.RISING, callback = blue_blinkEnable, bouncetime = 1000) #Calls Blue Button Function
    GPIO.add_event_detect(yButton, GPIO.RISING, callback = yellow_blinkEnable, bouncetime = 1000) #Calls Yellow Button Function
    GPIO.add_event_detect(rButton, GPIO.RISING, callback = redandgreen_button, bouncetime = 1000) #Calls Red and Green Button Function
    GPIO.add_event_detect(gButton, GPIO.RISING, callback = redandgreen_button, bouncetime = 1000) #Calls Red and Green Button Function
#format is: button we are waiting for, rise of value, function to call when clicked, and recovery time
    
    while True:
        continue
    GPIO.cleanup() #Cleans ports
Interrupt() #Calls the Interrupt Functions