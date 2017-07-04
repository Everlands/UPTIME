#=================================================
#  Read the Uptime Robot Monitor Status, and Report       =
#=================================================

import json, requests
import colorama
from colorama import init, Fore, Back, Style
import os, random, string, time
import RPi.GPIO as GPIO
import yaml

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT

# This makes the ANSI colours work in Windows. Meh. 
if os.name == 'nt':
    init(convert=True)

# These arrays are used to convert a status number to text, and to select an appropriate colour
monitor_status = [ "Paused", "Not Checked", "Up","3","4","5","6","7","Apparently Down","Down"]
monitor_colour = [ Fore.WHITE + Style.DIM, Fore.WHITE + Style.NORMAL, Fore.GREEN + Style.BRIGHT, '', '', '', '', '', Fore.RED + Style.BRIGHT, Fore.RED + Style.BRIGHT]

#read the config data (YAML data format)
config = yaml.safe_load(open("uptime.yml"))

# Get the global API key for Uptime Robot
ur_api_key=config['ur_api_key']


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

    try:
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
    except:
        print(Fore.RED + Style.BRIGHT + "Could not retrieve monitors. Sorry."+ Fore.RESET + Style.RESET_ALL)
        return ""
        

# Display the status of each monitor.
# Argument is a json array of monitors
def showMonitors(monitors):

    if monitors != "":    
        # Loop through, decoding the status to appropriate colour and text
        for monitor in monitors:
            status = monitor['status'] 
            print(monitor_colour[status] + monitor['friendly_name'], "is", monitor_status[status] + Fore.RESET + Style.RESET_ALL)            
    else:
            print ('')
    
    print()

# Count the "down" monitors and alert!
# Argument is a json array of monitors
def countMonitors(monitors):
       
    downs = 0

    if monitors != "": 
        for monitor in monitors:
            status = monitor['status']
            if status=="9":
                downs=downs+1
    # if there are some apps down, flash a light
        if downs > 0:
            blink(10,.5)
    else:
        # A value of -1 indicates that no count could be set.
        downs = -1

    return (downs)

# Turn the count into a nice bit of human readable text.
# Argument is an integer
def textDownCount(downs) :       
    if downs == -1:
        return ('')
    elif downs==0:
        return ('There are no applications down')
    elif downs == 1:
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
downs = countMonitors(Monitors)
print(textDownCount(downs))


GPIO.cleanup()    
print()
