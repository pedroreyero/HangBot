import random
import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import time
import math
import dibuixa


def nre_paraules(fitxer): #Retorna el nre de paraules del diccionari
    fe=open(fitxer,'r')   #Tambe es pot fer len(fe.readlines())
    comptador=0           #El fitxer ha d'estar filtrat:
    for linia in fe:      #paraules en MAJ i 2-7 lletres.
        comptador+=1
    return comptador

def gen_paraules(fitxer): #Retorna un generador de paraules
    fe=open(fitxer,'r')
    for linia in fe:
         paraula=linia.strip()
         yield paraula

def escull_paraula(fitxer): #Retorna una paraula aleatoria del diccionari
    it=gen_paraules(fitxer)
    longitud=nre_paraules(fitxer)
    num_par=random.randrange(0,longitud,1)
    i=0
    while i<num_par:
        next(it)
        i+=1
    return next(it)

def dic_ninot(): #Crea el diccionari del ninot
    d={1:'h1',2:'v1',3:'h2',4:'diag',5:'v2',6:'cap',7:'tronc',8:'bracos',9:'cama1',10:'cama2'}
    return d

def inicialitzar(settings):
	# Establish a serial connection to the dynamixel network.
	# This usually requires a USB2Dynamixel
	serial = dynamixel.SerialStream(port=settings['port'],
					baudrate=settings['baudRate'],
					timeout=1)
    	# Instantiate our network object
    	net = dynamixel.DynamixelNetwork(serial)

    	# Populate our network with dynamixel objects
    	for servoId in settings['servoIds']:
    	    	newDynamixel = dynamixel.Dynamixel(servoId, net)
    	    	net._dynamixel_map[servoId] = newDynamixel
    
    	if not net.get_dynamixels():
      		print "No s'han trobat motors!"
      		sys.exit(0)
    	else:
      		print "Motors ok!"
    	
	# Movem a la posicio inicial al robot
    	dibuixa.punt(0,0,-150, 100, net)
	return net

def generar_settings():
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean", default=False,
                      help="Ignore the settings.yaml file if it exists and \
                      prompt for new settings.")
    
    (options, args) = parser.parse_args()
    
    # Look for a settings.yaml file
    settingsFile = 'settings.yaml'
    if not options.clean and os.path.exists(settingsFile):
        with open(settingsFile, 'r') as fh:
            settings = yaml.load(fh)
    # If we were asked to bypass, or don't have settings
    else:
        settings = {}
        
        settings['port'] = "/dev/ttyUSB0"
        
        # Baud rate
        baudRate = None
        while not baudRate:
            brTest = raw_input("Enter baud rate [Default: 1000000 bps]:")
            if not brTest:
                baudRate = 1000000
            else:
                baudRate = validateInput(brTest, 9600, 1000000)
                    
        settings['baudRate'] = baudRate
        
        # Servo ID
        highestServoId = None
        while not highestServoId:
            hsiTest = raw_input("Please enter the highest ID of the connected servos: ")
            highestServoId = validateInput(hsiTest, 1, 255)
        
        settings['highestServoId'] = highestServoId


        highestServoId = settings['highestServoId']

        # Establish a serial connection to the dynamixel network.
        # This usually requires a USB2Dynamixel
        serial = dynamixel.SerialStream(port=settings['port'],
                                        baudrate=settings['baudRate'],
                                        timeout=1)
        # Instantiate our network object
        net = dynamixel.DynamixelNetwork(serial)
        
        # Ping the range of servos that are attached
        print "Scanning for Dynamixels..."
        net.scan(1, highestServoId)

        settings['servoIds'] = []
        print "Found the following Dynamixels IDs: "
        for dyn in net.get_dynamixels():
            print dyn.id
            settings['servoIds'].append(dyn.id)

        # Make sure we actually found servos
        if not settings['servoIds']:
          print 'No Dynamixels Found!'
          sys.exit(0)

        # Save the output settings to a yaml file
        with open(settingsFile, 'w') as fh:
            yaml.dump(settings, fh)
            print("Your settings have been saved to 'settings.yaml'. \nTo " +
                   "change them in the future either edit that file or run " +
                   "this example with -c.")

    return settings


def validateInput(userInput, rangeMin, rangeMax):
    '''
    Returns valid user input or None
    '''
    try:
        inTest = int(userInput)
        if inTest < rangeMin or inTest > rangeMax:
            print "ERROR: Value out of range [" + str(rangeMin) + '-' + str(rangeMax) + "]"
            return None
    except ValueError:
        print("ERROR: Please enter an integer")
        return None
    
    return inTest



def joc(fitxer_dicc): 

    settings = generar_settings()
    net = inicialitzar(settings)

    dibuixa.punt(0, 0, -150, 50, net)
    raw_input("Posa el boli i pressiona Enter")

    par=escull_paraula(fitxer_dicc) # Per ex. 'MARIA'
    ll_encerts=list(par) # ['M','A','R','I','A']
    caselles=(['']*len(par)) # Ha de dibuixar 5 rectes
    
    dibuixa.linies(len(par), net) # Dibuixa les caselles

    dic_dibuix=dic_ninot() # {1:'h1', etc}
    errors=0
    lletres_erronies=set()

    omplint = (['']*len(par)) 
    print(omplint)

    while errors < 10: # Les 10 parts del penjat o intents
        intent=raw_input('Entra una lletra: ').upper()
	if not intent.isalpha() or len(intent) != 1:
	    print "No has entrat una lletra!"
	    continue
        elif intent not in ll_encerts:   # Intent filtrat a lletres
            errors += 1

	    dibuixa.penjat(errors,net)     # Dibuixa la part del ninot
	    pos_er = 7 + errors
	    dibuixa.lletra(intent, pos_er, net)    # Dibuixa la lletra

            lletres_erronies.add(intent)  # S'apunta la lletra erronia
            #print(intent)                

        else:
            pos=[]
            for i in range (0, len(ll_encerts)):
                if ll_encerts[i]==intent:
                    pos.append(i+1)     # Les posicions comencen en 1
                    ll_encerts[i]=''
                    omplint[i]=intent

	    for i in pos:
		dibuixa.lletra(intent,i,net)

            #print(pos)         # Dibuixa les lletres a aquestes posicions
	    #print(ll_encerts)  #  si el jugador diu una lletra bona 2 cops
            #print(caselles)    #  la segona es comptara com a dolenta
            
            print(omplint)
            if ll_encerts==caselles:
                print('HAS GUANYAT')
                break

    if errors==10:
        print('HAS PERDUT')
	print('Ara el robot acabara la paraula')
	for i in range(len(ll_encerts)):
		intent = ll_encerts[i]	     # Quan perd acaba la paraula
		if intent != '':
			dibuixa.lletra(intent, i+1, net)
	print('La paraula era', par)
        
    dibuixa.punt(0,0,-150,50,net)    # Torna a la posicio inicial
       







