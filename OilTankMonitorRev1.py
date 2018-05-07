# name:     OilTank.py
# Version:  rev. 1
# Date:     28/04/2018
# Author:   Brian Hickey, x17126622 with help from below
# Reference:    https://code-maven.com/slides/python-programming/sqlite-insert
#               https//stackoverflow.com-Why the need to commit explicitly when doing an UPDATE?
#               Class work and presentations e.g. SQLite.py exercise.
#               https://docs.python.org/2/library/datetime.html
#               This python file is very much a mis-match of different examples of using different operations
#               and adapting them to the code needed for the project.
#               Learning and using datetime is an example of this
#               Email code (def emailalarm, http://stackabuse.com/how-to-send-emails-with-gmail-using-python/
#

from grovepi import *

import datetime
import time
import sqlite3
import smtplib
from grove_rgb_lcd import *


def emailalarm():                               #email level alarm is activated. Disabled after email is sent.
    gmail_user = 'user'
    gmail_password = 'passwd'

    sent_from = gmail_user
    to = ['receive email address']
    subject = 'The Oil Tank is below 20 Litres'
    body = 'Get oil!'
                                                #This code was sourced online. See references
    email_text = """\                           
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:                                        #Try to send and if good print email sent, else print something went wrong
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print ('Email sent!')
        
    except:
        print ('Something went wrong...')
  



SensorEnable = True         #SensorEnable set to true. Coded this way to allow for enable/disable function if needed
value = 0                   #Initiate the value variable used in the readsensor function
sensor = []                 #Initialize array for the sensor readings
lowLevelAlarm = False       #Initialize the lowlevel alarm bit
LowLevelCount = 0           #Initialize the lowlevel count for the low level alarm
LowLevel = 20               #initialize the low level value in litres
ultrasonic_ranger = 4       #Set the input port for the ultrasonic sensor
relay = 2		            #Port for relay
button = 3		            #Port for Button
average = 0                #Set the average value to 0. Used in getting average sensor reading
emailEnable = True          # Set email enable to true at startup
RedLED = 8                  #Port for RED LED
pinMode(relay,"OUTPUT")	# Assign mode for buzzer as output  #Set port for the relay as an output
pinMode(button,"INPUT")		# Assign mode for Button as input   #set the port for the button as input


# readsensor function
def readsensor(value):

    for x in range(5):
        total = 0                               # reset the current total
        SensorReading = ultrasonicRead(ultrasonic_ranger)                     # current reading
        MaxSensor = 70.0                       # maximum value in range from sensor
        MinSensor = 2.0                         # minimum value in range from sensor
        minOffset = MaxSensor - MinSensor       # calculate the span of the range
        litreRange = 900.0                      # The range of the tank in litres
        tempvalue = (((SensorReading - minOffset) - MinSensor) * -1)    # convert value max to min to min to max
        multiplier = litreRange / MaxSensor                             # calculate multiplier (slope)
        litres = tempvalue * multiplier                                 # convert to litres
        total = total + litres                                          # get 5 results for average
    return total





# Use a while loop to constantly read the current time
while SensorEnable:
   
    button_status= digitalRead(button)	#Read the Button status	
		
    if button_status:
                     
                    setRGB(0,255,0)         #set display background
                    buf=["Current level: \n", str(average), " Litres"]  #write the current value to the display. Only done after first reading from sensor
                    setText("".join(buf))
                    time.sleep(10)                                      #wait 10secs and turn off display
                    setRGB(0,0,0)
                    buf=["Press to check  level"]                       #This text is shown but without backlight
                    setText("".join(buf))
      # If a low level alarm occurs, only allow heat on between 18:00 and 22:00              
    if lowLevelAlarm and datetime.datetime.now().hour>18 and datetime.datetime.now().hour<22:
                    digitalWrite(relay,1)
    else:
                    digitalWrite(relay,0)
                    
    if lowLevelAlarm:
                    digitalWrite(RedLED,1)
    else:
                    digitalWrite(RedLED,0)
                    
                    
    # Check if the time is on quarter hour.    
    while ((datetime.datetime.now().minute == 00) or (datetime.datetime.now().minute == 15) or
           (datetime.datetime.now().minute == 30) or (datetime.datetime.now().minute == 45)):
        # get the Sensor reading
        total = readsensor(value)
        dt = datetime.datetime.now()
        date = dt.strftime("%y-%m-%d")
        timenow = dt.strftime("%H:%M")      
        minute = dt.minute
        sensor.append(total)

        if len(sensor) > 4:                     #if 5 readings
            print (timenow)                     #for testing: print timenow
            print (sum(sensor) / len(sensor))   #print measured value
            average = sum(sensor) / len(sensor) #compute average of readings
            connection = sqlite3.connect("TankLevel.db")    #connect to database(sqlite)
            cursor = connection.cursor()                    #Initialize cursor
            cursor.execute('''INSERT INTO level (Date, Time, Level) VALUES (?, ?, ?)''', (date, timenow, average,)) #Put the date, timenow and average reading into the database
            if average < LowLevel : #If read value is lower than low value
                LowLevelCount += 1  #add one to lowlevelcount
            if LowLevelCount >= 3:  #if lowlevel count is greater or equal to 3, enable lowlevel alarm
                lowLevelAlarm = True    #Low level alarm is true
            if lowLevelAlarm and emailEnable:       #if lowlevel alarm and email has not already been sent, call email function
                emailalarm()                        #call email function
                emailEnable = False                 #Email has been sent, disable email
            print (lowLevelAlarm)                   #for testing print status of lowlevel alarm
            print (LowLevelCount)                   #print lowlevel count
            print (emailEnable)                     #print if email enable is true
            connection.commit()                     #commit changes to the database
            cursor.close()                          #close the cursor for the database
            connection.close()                      #close the connection to the database
            sensor = []                             #clear the sensor array values
            time.sleep(60)                          #wait 60 seconds. this is to wait for the time to update by one 1 minute
            

 
            

       
            

