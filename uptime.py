#=================================================
#  Read the Uptime Robot Monitor Status, and Report       =
#=================================================

import json, requests
import colorama
from colorama import init, Fore, Back, Style
import os, random, string, time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT

# This makes the ANSI colours work in Windows. Meh. 
if os.name == 'nt':
    init(convert=True)

# These arrays are used to convert a status number to text, and to select an appropriate colour
monitor_status = [ "Paused", "Not Checked", "Up","3","4","5","6","7","Apparently Down","Down"]
monitor_colour = [ Fore.WHITE + Style.DIM, Fore.WHITE + Style.NORMAL, Fore.GREEN + Style.BRIGHT, '', '', '', '', '', Fore.RED + Style.BRIGHT, Fore.RED + Style.BRIGHT]

# The global API key for Uptime Robot
ur_api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'


#=================================================
# Function Definitions                                                            =
#=================================================

# Clear the Terminal Window
def clearScreen():    
    os.system('cls' if os.name == 'nt' else 'clear')

# This function returns a random string of characters
def randomWord(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

# Call the UptimeRobot API and get a list of Monitors back
def getMonitors():

    print (Fore.CYAN + Style.BRIGHT +  'Fetching Uptime Robot Data' + Fore.RESET + Style.RESET_ALL)
    print('')

    # Set up the request
    url = 'https://api.uptimerobot.com/v2/getMonitors'
     
    payload = 'api_key=' + ur_api_key + '&format=json&logs=1&rnd=' + randomWord(10) #Adding random word makes sure it's not cached
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }

    # Make the call 
    response = requests.request('POST', url, data=payload, headers=headers)

    # Decode the response 
    jsonData = json.loads(response.text)

    # Only want the 'monitors' json array
    monitors = jsonData['monitors']

    return monitors

# Display the status of each monitor
def showMonitors(monitors):
    
    # Loop through, decoding the status to appropriate colour and text
    for monitor in monitors:
        status = monitor['status'] 
        print(monitor_colour[status] + monitor['friendly_name'], "is", monitor_status[status] + Fore.RESET + Style.RESET_ALL)            
        
    print()

# Count the "down" monitors and alert!
def countMonitors(monitors):
       
    downs = 0
    
    for monitor in monitors:
        status = monitor['status']
        if status=="9":
            downs=downs+1

    if downs > 0:
        blink(10,.5)
        
    if downs == 1:
        return ('There is 1 application down')
    else:
        return ('There are ' +  str(downs) + ' applications down')   

    
# This flashes an LED on pin 7
def blink(numTimes, speed):
    for i in range(0, numTimes):        
        GPIO.output(7, True)
        time.sleep(speed)
        GPIO.output(7, False)
        time.sleep(speed)
    
#=================================================
# App Starts Here                                                                    =
#=================================================

clearScreen()    
Monitors = getMonitors()
showMonitors(Monitors)
print (countMonitors(Monitors))

GPIO.cleanup()    
print()
