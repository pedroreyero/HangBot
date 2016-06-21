from __future__ import division
import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import time
import math

# PARAMETRES GENERALS EN EL DIBUIX DE LES LLETRES I LES SEVES LINIES
espai_intermig = 10
espai_intermig_error = 10
espai_interlinia_error = 10
centre1 = (-130,-50)
centre_error1 = (-160,90)
a = 30
b = 50


l_centres = []
for i in range(7):
	l_centres.append( (centre1[0] + i * (a + espai_intermig), centre1[1]) )
for i in range(10):
	if i < 5:
		l_centres.append( (centre_error1[0] + i * (a + espai_intermig_error),
				   centre_error1[1]) )
	else:
		l_centres.append( (centre_error1[0] + (i-5) * (a + espai_intermig_error),
				   centre_error1[1] - b - espai_interlinia_error) )


#PROGRAMA ADRILUQUE CINEMATICA INVERSA INVKIN

pi = math.pi
cos120 = math.cos(2/3 * pi)
sin120 = math.sin(2/3 * pi)

def sqrt(x):
	return math.sqrt(x)

# PARAMETRES ---------------------------------

f=150
falt = 2*f/math.tan(pi/6)
e=125
ealt = 2*e/math.tan(pi/6)
ealt=2*e/math.tan(pi/6)
rf=205
re=329

# CINEMATICA INVERSA -------------------------

def angleYZ(x0, y0, z0):
    y1 = - falt/2 * math.tan(pi/6)      
    y0 -= 0.5 * math.tan(pi/6) * ealt   #Canvi del centre al borde
    #z = A + By
    A = (x0**2 + y0**2 + z0**2 + rf**2 - re**2 - y1**2)/(2*z0)
    B = (y1-y0)/z0
    #Discriminant
    d = -(A+B*y1)**2 + rf*(B**2*rf + rf)
    if d<0:
        return -1     #No existeix el punt!
    else:
        yj = (y1 - A*B - math.sqrt(d))/(B**2 + 1)
        zj = A + B*yj
        theta = math.atan(-zj/(y1-yj))
        theta = 180/pi * theta
        return theta
    
def KInv(x0,y0,z0):
    theta1 = angleYZ(x0, y0, z0)
    theta2 = angleYZ(x0*cos120 + y0*sin120, y0*cos120 - x0*sin120, z0)
    theta3 = angleYZ(x0*cos120 - y0*sin120, y0*cos120 + x0*sin120, z0)
    if theta1==-1 or theta2==-1 or theta3==-1:
	print "ERROR!"
        return "ERROR!"
    else:
        return theta1, theta2, theta3

def angles(x0, y0, z0):
    th = KInv(x0, y0, z0)
    a1 = int(th[0] * 512/150 + 512)
    a2 = int(th[1] * 512/150 + 512)
    a3 = int(th[2] * 512/150 + 512)
    return a1, a2, a3


#----------------------------------------------

""" 
This script will discover available USB ports to which the USB2Dynamixel may
be attached. It will also help you discover the list of servos that are in the
network. Once that has been done these values will be stored in  a local
settings.yaml file.

You will then be shown all of the found servo ids.
"""

# FUNCIO QUE DIBUIXA UN PUNT ----------------------------
def punt(posicio_x, posicio_y, posicio_z, velocitat, net):
	
	"""
	Dibuixa un punt en la posicio 'posicio', anant-hi a velocitat 'velocitat' (entre 0 i 1023).
	"""
		
	if velocitat in range(0,1024):
		pass
	else:
		raise ValueError # La velocitat demanada no es correcta :(
	
	th1,th2,th3 = angles(posicio_x, posicio_y, posicio_z)
	th = [th1,th2,th3]
	i = 0
		
        for actuator in net.get_dynamixels():
            actuator.moving_speed = velocitat
            actuator.torque_enable = True
            actuator.torque_limit = 800 
            actuator.max_torque = 800
            actuator.goal_position = th[i]
	    i += 1

        net.synchronize()

	return net


# FUNCIO QUE DIBUIXA UNA LLETRA ----------------------------
def lletra(lletra, posicio, net):
	
	"""
	Dibuixa la lletra 'lletra' en la posicio 'posicio', entre 1 i 7, de la paraula 		triada. Si la lletra entrada es erronia, el parametre 'posicio' estara entre
	8 i 17 (ve del programa de joc), i es dibuixara a la taula d'errors.
	"""	

	lletra_neta = lletra.strip().lower()
	if posicio >= 8: # Volem dibuixar un error
		d_error = {8: 17, 9: 12, 10: 16, 11: 11, 12: 15, 13: 10, 14: 14, 15: 9, 16: 13, 17: 8}
		posicio = d_error[posicio]
	centre = l_centres[posicio-1]

	# INICI
	d_posicions_inicials = {'a': (-a/2,-b/2),'b': (-a/2,-b/2),'c': (a/2,b/2),'d': (-a/2,-b/2),
				'e': (a/2,b/2),'f': (-a/2,-b/2),'g': (0,0),'h': (-a/2,-b/2),
				'i': (-a/2,b/2),'j': (-a/2,b/2),'k': (-a/2,-b/2), 'l': (-a/2,b/2),
				'm': (-a/2,-b/2),'n': (-a/2,-b/2),'o': (a/2,0),'p': (-a/2,-b/2),
				'q': (a/2,0),'r': (-a/2,-b/2),'s': (a/2,b/2),'t': (-a/2,+b/2),
				'u': (-a/2,b/2),'v': (-a/2,b/2),'w': (-a/2,b/2),'x': (-a/2,b/2),
				'y': (-a/2,b/2),'z': (-a/2,b/2)}
	pos_ini = d_posicions_inicials[lletra_neta]
	d_posicions_finals = {'a': (a/4,0),'b': (-a/2,-b/2),'c': (a/2,-b/2),'d': (-a/2,-b/2),
				'e': (0,0),'f': (0,0), 'g': (a/(2*sqrt(2)), b/(2*sqrt(2))),'h': (a/2,b/2),
				'i': (a/2,-b/2),'j': (-a/2,0),'k': (a/2,-b/2), 'l': (a/2,-b/2),
				'm': (a/2,-b/2),'n': (a/2,b/2),'o': (a/2,0),'p': (-a/2,0),
				'q': (a/2,-b/2),'r': (a/2,-b/2),'s': (-a/2,-b/2),'t': (0,-b/2),
				'u': (a/2,b/2),'v': (a/2,b/2),'w': (a/2,b/2),'x': (a/2,b/2),
				'y': (0,-b/2),'z': (a/4,0)}
	pos_fi = d_posicions_finals[lletra_neta]
	th1,th2,th3 = angles(pos_ini[0] + centre[0], pos_ini[1] + centre[1], -180)
	th = [th1,th2,th3]
	j = 0
	
        for actuator in net.get_dynamixels():
		actuator.moving_speed = 100
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

	net.synchronize()
	time.sleep(2)
	
	th1,th2,th3 = angles(pos_ini[0] + centre[0], pos_ini[1] + centre[1], -220)
	th = [th1,th2,th3]
	j = 0
		
	for actuator in net.get_dynamixels():
		actuator.moving_speed = 40
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	time.sleep(1)

	# LLETRA
	#TODO - Ajustar posicions 7, 8, 17

	if lletra_neta == 'a':
		## Lletra A --------------------------------------------------
		#Tram 1 - Diag.Esq.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-230,-215,-215,-215,-227,-227,-215,-215,-227,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/(2*num_punts) * i
			yi = b * ((2*xi)/a + 1/2)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.3,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		
		# Tram 2 - Diag.Dret
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-230,-215,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
			xi = 0 + a/(2*num_punts) * i
			yi = -b * ((2*xi)/a - 1/2) 

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.3,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])


		# Resituacio
		time.sleep(0.4)
		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -190)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/4 + centre[0], 0 + centre[1], -190)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])	
	

		# Tram 3 - Horitzontal
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = 3
		l_altures = [-227,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/4 + a/(2*num_punts) * i
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
	if lletra_neta == 'b':
		## Lletra B --------------------------------------------------
		# TODO: Ajustar posicio 7
		# Tram 1 - Vertical
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-225,-225,-225,-225,-227,-230,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b * i / num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		
		# Tram 2 - Horit.Alt
		time.sleep(0.3)
		l_punts = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i / num_punts
			yi = +b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])


		# Tram 3 - Primera Corba
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
			zita = pi/2 - pi * i /num_punts
			xi = 0 + a/2 * math.cos(zita)
			yi = b/4 + b/4 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
			time.sleep(l_sleep[posicio-1])


		# Tram 4 - Horit.Mig
		l_punts = [3,3,3,3,3,6,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 - a/2 * i / num_punts
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])

		
		# Tram 5 - Horit.Mig
		l_punts = [3,3,3,3,3,6,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i / num_punts
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])


		# Tram 6 - Segona Corba
		time.sleep(0.3)
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
			zita = pi/2 - pi * i /num_punts
			xi = 0 + a/2 * math.cos(zita)
			yi = -b/4 + b/4 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
			time.sleep(l_sleep[posicio-1])


		# Tram 7 - Horit.Baix
		l_punts = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-227,-227,-227,-227,-227,-230,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 - a/2 * i / num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
	if lletra_neta == 'c':
		## Lletra C --------------------------------------------------
		# Tram 1 - Horit.Alt
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-228,-228,-228,-228,-228,-228,-228,-220,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/4 - a/(4*num_punts) * i
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		
		# Tram 2 - Corba
		l_punts = [60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60]
		num_punts = l_punts[posicio-1]
		l_altures = [-228,-228,-228,-228,-228,-228,-228,-220,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
			zita = pi/2 + pi * i /num_punts
			xi = 0 + a/2 * math.cos(zita)
			yi = 0 + b/2 * math.sin(zita) 

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		
		net.synchronize()
		l_sleep = [0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4]
		time.sleep(l_sleep[posicio-1])	
	

		# Tram 3 - Horit.Baix
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-228,-228,-228,-228,-228,-228,-228,-220,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 + a/4 * i / num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
	if lletra_neta == 'd':
		## Lletra D --------------------------------------------------
		# Tram 1 - Vertical
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
	

		# Tram 2 - Horit.Alt
		time.sleep(0.4)
		l_punts = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2]
			time.sleep(l_sleep[posicio-1])
		
		# Tram 3 - Corba
		time.sleep(0.4)
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
		    zita = pi/2 - pi * i/num_punts
		    xi = 0 + a/2 * math.cos(zita)
		    yi = 0 + b/2 * math.sin(zita) 
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
		    time.sleep(l_sleep[posicio-1])


		# Tram 4 - Horit.Baix
		time.sleep(0.4)
		l_punts = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 - a/2 * i/num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'e':
		## Lletra E --------------------------------------------------
		# Tram 1 - Alt
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
		    xi = a/2 - a * i/num_punts
		    yi = b/2
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]   		
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
	
		time.sleep(1)

		# Tram 2 - Vertical
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
		    xi = -a/2
		    yi = b/2 - b * i/num_punts
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]   		
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
	
		time.sleep(1)

		# Tram 3 - Baix
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
		    xi = -a/2 + a * i/num_punts
		    yi = -b/2
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]   		
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
	
		time.sleep(1)

		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1
    		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])
	
	
		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])


		# Tram 4 - Mig
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
		    xi = -a/2 + a/2 * i/num_punts
		    yi = 0
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]   		
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'f':
		## Lletra F --------------------------------------------------
		# Tram 1 - Vertical
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
		    xi = -a/2
		    yi = -b/2 + b * i/num_punts
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]   		
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
	
		time.sleep(1)

		# Tram 2 - Horit.Alt
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
		    xi = -a/2 + a/num_punts * i
		    yi = b/2
     		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1],l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		    for actuator in net.get_dynamixels():
		        actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])

		time.sleep(0.5)
	
		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1
    		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])
	
	
		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1
		net.synchronize()
		l_sleep = [2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5]
		time.sleep(l_sleep[posicio-1])
	

		# Tram 3 - Horit.Mig
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
		    xi = -a/2 + a/(2*num_punts)*i
		    yi = 0 
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.2,0.1,0.1,0.1,0.1,0.2,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
	

	if lletra_neta == 'g':
		## Lletra G --------------------------------------------------
		# Tram 1 - Horit.Mig
		l_punts = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
		    xi = 0 + a/2 * i/num_punts
		    yi = 0 
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		    time.sleep(l_sleep[posicio-1])

		# Tram 2 - Corba
		time.sleep(0.4)
		l_punts = [100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
		    zita = 0 - 7/4 * pi * i /num_punts
		    xi = 0 + a/2 * math.cos(zita)
		    yi = 0 + b/2 * math.sin(zita)
		    th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
		    th = [th1,th2,th3]
		    j = 0
		    l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		    for actuator in net.get_dynamixels():
		    	actuator.moving_speed = l_speed[posicio-1]
		    	actuator.torque_enable = True
		    	actuator.torque_limit = 800 
		    	actuator.max_torque = 800
		    	actuator.goal_position = th[j]
		    	j += 1
		    net.synchronize()
		    l_sleep = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
		    time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'h':
		## Lletra H --------------------------------------------------
		# Tram 1 - Vert.Esq.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio
		th1,th2,th3 = angles(-a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])	

		# Tram 2 - Horitzontal
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a*i/num_punts
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])	
		
		# Resituacio2
		time.sleep(0.5)
		th1,th2,th3 = angles(a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	


		# Tram 3 - Vert.Dret
		l_punts = [15,15,15,15,15,15,15, 7,15,15,15,15, 5,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-230,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2
			yi = -b/2 + b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 1000 
		    		actuator.max_torque = 1000
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1, 0.2,0.1,0.1,0.1,0.1, 0.2,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
	
		
	if lletra_neta == 'i':
		## Lletra I --------------------------------------------------
		# Tram 1 - Horit.Alt
		l_punts = [8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio
		time.sleep(0.4)
		th1,th2,th3 = angles(a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		net.synchronize()
		l_sleep = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	

		
		time.sleep(0.4)
		th1,th2,th3 = angles(0 + centre[0], b/2 + centre[1], -220)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	


		# Tram 2 - Vertical
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])	

		# Resituacio2
		time.sleep(0.4)
		th1,th2,th3 = angles(0 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	


		th1,th2,th3 = angles(-a/2 + centre[0], -b/2 + centre[1], -200)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])


		# Tram 3 - Horit.Baix
		l_punts = [8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------
		

	if lletra_neta == 'j':
		## Lletra J --------------------------------------------------
		# Tram 1 - Horit.Alt
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	

		# Tram 2 - Vertical
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0
			yi = b/2 - 3/4*b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])	

		# Tram 3 - Corba
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(1,num_punts+1):
			zita = 0 - pi * i /num_punts
			xi = -a/4 + a/4 * math.cos(zita)
			yi = -b/4 + b/4 * math.sin(zita) 

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		
		net.synchronize()
		l_sleep = [0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6]
		time.sleep(l_sleep[posicio-1])	
	
		# Tram 4 - Vertical Petit Esq.
		l_punts = [5,5,5,5,5,5,5, 5,2,2,5,5, 2,2,2,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/4 + b/4 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])	
		#------------------------------------------------------


	if lletra_neta == 'k':
		## Lletra K --------------------------------------------------
		# Tram 1 - Vertical
		l_punts = [15,15,15,15,15,15,15,15,18,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-227,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1, 0.1,0.3,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio
		th1,th2,th3 = angles(-a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	

		# Tram 2 - Diag.1
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = 0 + b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio2
		th1,th2,th3 = angles(a/2 + centre[0], b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	

		# Tram 3 - Diag.2
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = 0 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'l':
		## Lletra L --------------------------------------------------
		# Tram 1 - Vertical
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = b/2 - b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		time.sleep(1)

		# Tram 2 - Horitzontal
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'm':
		## Lletra M --------------------------------------------------
		# Tram 1 - Vert.Esq.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Diagonal 1
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i/num_punts
			yi = b/2 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Diagonal 2
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 + a/2 * i/num_punts
			yi = 0 + b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 4 - Vert.Dret.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2
			yi = b/2 - b*i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'n':
		## Lletra N --------------------------------------------------
		# Tram 1 - Vert.Esq.
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-225,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Diagonal
		time.sleep(0.4)
		l_punts = [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-225,-227,-227,-227,-227,-227,-225,-225,-230,-227,-227,-225,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Vert.Dret
		time.sleep(0.4)
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-225,-227,-227,-227,-227,-227,-225,-225,-230,-227,-227,-225,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'o':
		## Lletra O --------------------------------------------------
		# Tram 1a - Cercle
		l_punts = [100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0, num_punts+1):
			zita = 0 + 2*pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = 0 + b/2 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		"""
		# Tram 1b - Cercle (3/4)
		l_punts = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
		num_punts = l_punts[posicio-1]
		l_altures = [-223,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        zita = pi/2 + 3*pi/2 * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = 0 + b/2 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		"""
		#------------------------------------------------------


	if lletra_neta == 'p':
                ## Lletra P --------------------------------------------------
                # Tram 1 - Vertical
                l_punts = [25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25]
                num_punts = l_punts[posicio-1]
                l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
                for i in range(0,num_punts+1):
                        xi = -a/2
                        yi = -b/2 + b * i/num_punts

                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
         
                        l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]          
                                j += 1
 
             
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])
 
                time.sleep(1)       

                # Tram 2 - Horit.Alt
                l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
                num_punts = l_punts[posicio-1]
                l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
                for i in range(0,num_punts+1):
                        xi = -a/2 + a/2 * i/num_punts
                        yi = b/2
 
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        
                        l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]          
                                j += 1
 
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])

                # Tram 3 - Corba
                l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
                num_punts = l_punts[posicio-1]
                l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
                for i in range(1,num_punts+1):
                        zita = pi/2 - pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = b/4 + b/4 * math.sin(zita) 
                        
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]
                                j += 1
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])

                # Tram 4 - Horit. Mig
                l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
                num_punts = l_punts[posicio-1]
                l_altures = [-227,-227,-227,-227,-227,-227,-220,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
                for i in range(1,num_punts+1):
                        xi = 0 - a/2 * i/num_punts
                        yi = 0 
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]
                                j += 1
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])
                #------------------------------------------------------


	if lletra_neta == 'q':
		## Lletra Q --------------------------------------------------
		# Tram 1a - Cercle (1/4)
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-220,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0, num_punts+1):
			zita = 0 + pi/2 * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = 0 + b/2 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		# Tram 1b - Cercle (3/4)
		l_punts = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
		num_punts = l_punts[posicio-1]
		l_altures = [-223,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        zita = pi/2 + 3*pi/2 * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = 0 + b/2 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])


		# Resituacio
		time.sleep(0.3)
		th1,th2,th3 = angles(a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])

		
		th1,th2,th3 = angles(0 + centre[0], 0 + centre[1], -210)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])


		# Tram 2 - Recta
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        xi = 0 + a/2 * i/num_punts
                        yi = 0 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
                #------------------------------------------------------


	if lletra_neta == 'r':
                ## Lletra R --------------------------------------------------
                # Tram 1 - Vertical
                l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
                num_punts = l_punts[posicio-1]
                l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
                for i in range(0,num_punts+1):
                        xi = -a/2
                        yi = -b/2 + b * i/num_punts

                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
         
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]          
                                j += 1
 
             
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])     


                # Tram 2 - Horit.Alt
		time.sleep(0.4)
                l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
                num_punts = l_punts[posicio-1]
                l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
                for i in range(0,num_punts+1):
                        xi = -a/2 + a/2 * i/num_punts
                        yi = b/2
 
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]          
                                j += 1
 
                        net.synchronize()
                        l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
                        time.sleep(l_sleep[posicio-1])

                # Tram 3 - Corba
                l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,40,20,20,20,20]
                num_punts = l_punts[posicio-1]
                l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
                for i in range(1,num_punts+1):
                        zita = pi/2 - pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = b/4 + b/4 * math.sin(zita)
                        
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]
                                j += 1
                        net.synchronize()
                        l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.05,0.1,0.1,0.1]
                        time.sleep(l_sleep[posicio-1])

                # Tram 4 - Horit. Mig
                l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
                num_punts = l_punts[posicio-1]
                l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
                for i in range(1,num_punts+1):
                        xi = 0 - a/2 * i/num_punts
                        yi = 0 
                        th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
                        th = [th1,th2,th3]
                        j = 0
                        l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
                        for actuator in net.get_dynamixels():
                                actuator.moving_speed = l_speed[posicio-1]
                                actuator.torque_enable = True
                                actuator.torque_limit = 800
                                actuator.max_torque = 800
                                actuator.goal_position = th[j]
                                j += 1
                        net.synchronize()
                        l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.3,0.3,0.15,0.15,0.3,0.15,0.15,0.15,0.15]
                        time.sleep(l_sleep[posicio-1])
	
		# Resituacio
		time.sleep(0.3)
		th1,th2,th3 = angles(-a/2 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,80,80,50,50,80,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,90,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])

		
		th1,th2,th3 = angles(0 + centre[0], 0 + centre[1], -210)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,70,30,30,30,30]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		time.sleep(l_sleep[posicio-1])	

	
		# Tram 5 - Diagonal
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-226,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        xi = 0 + a/2 * i/num_punts
                        yi = 0 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
                #------------------------------------------------------


	if lletra_neta == 's':
		## Lletra S --------------------------------------------------
		# Tram 1 - Horit.Alt
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2 - a/2 * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Corba Esq.
		time.sleep(0.4)
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        zita = pi/2 + pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = b/4 + b/4 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Corba Dreta
		l_punts = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        zita = pi/2 - pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = -b/4 + b/4 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])

		# Tram 4 - Horit.Baix
		time.sleep(0.4)
		l_punts = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 - a/2 * i/num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 't':
		## Lletra T --------------------------------------------------
		# Tram 1 - Horitzontal
		l_punts = [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], b/2 + centre[1], -200)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], b/2 + centre[1], -200)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], b/2 + centre[1], -220)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	


		# Tram 2 - Vertical
		l_punts = [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'u':
		## Lletra U --------------------------------------------------
		# Tram 1 - Vertical Esq.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = b/2 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Corba
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-225,-225,-230,-227,-227,-225,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
                        zita = -pi + pi * i/num_punts
                        xi = 0 + a/2 * math.cos(zita)
                        yi = 0 + b/2 * math.sin(zita)

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Vertical Dret
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-225,-225,-230,-227,-227,-225,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2
			yi = 0 + b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'v':
		## Lletra V --------------------------------------------------
		# Tram 1 - Diag. Esq.
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i/num_punts
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Diag. Dreta
		time.sleep(0.4)
		l_punts = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 + a/2 * i/num_punts
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'w':
		## Lletra W --------------------------------------------------
		# Tram 1 - Diag. Gran Esq.
		l_punts = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/4 * i/num_punts
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])


		# Tram 2 - Diag. Petita Esq.
		time.sleep(0.4)
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/4 + a/4 * i/num_punts
			yi = -b/2 + b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Diag. Petita Dreta
		time.sleep(0.4)
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 + a/4 * i/num_punts
			yi = 0 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 4 - Diag. Gran Dreta
		time.sleep(0.4)
		l_punts = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
		num_punts = l_punts[posicio-1]
		l_altures = [-225,-225,-225,-225,-225,-225,-225,-210,-225,-230,-227,-227,-220,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/4 + a/4 * i/num_punts
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'x':
		## Lletra X --------------------------------------------------
		# Tram 1 - Diagonal cap-a-baix
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-220,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])


		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	
	
		# Tram 2 - Diagonal cap-a-dalt
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-220,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = -b/2 + b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'y':
		## Lletra Y --------------------------------------------------
		# Tram 1 - Diagonal cap-a-baix
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i/num_punts
			yi = b/2 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])


		# Tram 2 - Vertical
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0
			yi = 0 - b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		
		# Resituacio
		th1,th2,th3 = angles(0 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(0 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])


		# Tram 3 - Diagonal cap-a-dalt
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = 0 + a/2 * i/num_punts
			yi = 0 + b/2 * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1],
                                             l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])
		#------------------------------------------------------


	if lletra_neta == 'z':
		## Lletra Z --------------------------------------------------
		# Tram 1 - Horit.Alt
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-210,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 2 - Diagonal
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = a/2 - a * i/num_punts
			yi = b/2 - b * i/num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

		# Tram 3 - Horit.Baix
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/2 + a * i/num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

                
                # TREURE COMETES PER INCLOURE TRAM 4, POSAR PER NO DIBUIXAR-LO
                # ALTERNAR TAMBE LES COMETES DEL FINAL DE LA Z!!
                # COM AL OPTC, Z DONA PROBLEMES...
		# Resituacio
		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]
		time.sleep(l_sleep[posicio-1])


		th1,th2,th3 = angles(-a/4 + centre[0], 0 + centre[1], -180)
		th = [th1,th2,th3]
		j = 0
		
		l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = l_speed[posicio-1]
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		
		net.synchronize()
		l_sleep = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
		time.sleep(l_sleep[posicio-1])	
                
		# Tram 4 - Horit.Baix
		l_punts = [30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
		num_punts = l_punts[posicio-1]
		l_altures = [-227,-227,-227,-227,-227,-227,-227,-210,-225,-230,-227,-227,-227,-225,-230,-227,-227]
		for i in range(0,num_punts+1):
			xi = -a/4 + a/2 * i/num_punts
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], l_altures[posicio-1])
			th = [th1,th2,th3]
			j = 0
		
			l_speed = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]
			for actuator in net.get_dynamixels():
		    		actuator.moving_speed = l_speed[posicio-1]
		    		actuator.torque_enable = True
		    		actuator.torque_limit = 800 
		    		actuator.max_torque = 800
		    		actuator.goal_position = th[j]   		
				j += 1

			net.synchronize()
			l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
			time.sleep(l_sleep[posicio-1])

                """
                # DEIXAR LES COMETES PER LES DUES OPCIONS
                # COM AL OPTC, Z DONA PROBLEMES...

		# "Pujadeta" (sense Tram 4 - Horit.Mig!!)
		th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -220)
		th = [th1,th2,th3]
		j = 0
		
		
		for actuator in net.get_dynamixels():
		    actuator.moving_speed = 20
		    actuator.torque_enable = True
		    actuator.torque_limit = 800 
		    actuator.max_torque = 800
		    actuator.goal_position = th[j]
		    j += 1

		net.synchronize()
		time.sleep(2)
		#------------------------------------------------------

                # POSAR COMETES AQUI TAMBE PER INCLOURE TRAM 4
                # NO FER-HO PER NO DIBUIXAR-LO
		"""

		#------------------------------------------------------

	# FI
	th1,th2,th3 = angles(pos_fi[0] + centre[0], pos_fi[1] + centre[1], -180)
	th = [th1,th2,th3]
	j = 0
		
	for actuator in net.get_dynamixels():
		actuator.moving_speed = 40
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	time.sleep(0.5)
		
	
	th1,th2,th3 = angles(0, 0, -150)
	th = [th1,th2,th3]
	j = 0
		
        for actuator in net.get_dynamixels():
            actuator.moving_speed = 100
            actuator.torque_enable = True
            actuator.torque_limit = 800 
            actuator.max_torque = 800
            actuator.goal_position = th[j]
	    j += 1

        net.synchronize()
	time.sleep(1)

#-----------------------------------------------------------

# FUNCIO QUE DIBUIXA LES PARTS DEL PENJAT ----------------------------
def penjat(tros, net):
	
	"""
	Dibuixa el tros 'tros', entre 1 i 10, del penjat.
	"""	
	
	a = 120
	b = 120
	centre = (100,60)

	pos_inicial = [(a/2,-b/2),(-a/2,-b/2),(-a/2,b/2),(-a/2,b/4),(0,b/2),(0,b/8),(0,b/8),(-a/4,0),(0,-b/4),(0,-b/4)]
	pos_final = [(-a/2,-b/2),(-a/2,b/2),(0,b/2),(-a/4,b/2),(0,3*b/8),(0,b/8),(0,-b/4),(a/4,0),(-a/4,-b/4),(a/4,-b/4)]

	# Posicionament
	th1,th2,th3 = angles(pos_inicial[tros-1][0] + centre[0], pos_inicial[tros-1][1] + centre[1], -180)
	th = [th1,th2,th3]
	j = 0
		
	for actuator in net.get_dynamixels():
		actuator.moving_speed = 100
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	time.sleep(2)

	th1,th2,th3 = angles(pos_inicial[tros-1][0] + centre[0], pos_inicial[tros-1][1] + centre[1], -220)
	th = [th1,th2,th3]
	j = 0
		
	for actuator in net.get_dynamixels():
		actuator.moving_speed = 40
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	time.sleep(1)

	
	# Tram en questio
	if tros == 1:	
		# Tram 1 - Base
		num_punts = 30
		altura = -228
		for i in range(0,num_punts+1):
			xi = a/2 - a * i / num_punts
			yi = -b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0
		
			for actuator in net.get_dynamixels():
				actuator.moving_speed = 50
				actuator.torque_enable = True
				actuator.torque_limit = 800 
				actuator.max_torque = 800
				actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			time.sleep(0.1)


	if tros == 2:
		# Tram 2 - Pilar
		num_punts = 15
		altura = -228
		for i in range(0,num_punts+1):
			xi = -a/2
			yi = -b/2 + b * i / num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0
		
			for actuator in net.get_dynamixels():
				actuator.moving_speed = 50
				actuator.torque_enable = True
				actuator.torque_limit = 800 
				actuator.max_torque = 800
				actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			time.sleep(0.2)


	if tros == 3:				
		# Tram 3 - Superior
		num_punts = 15
		altura = -228
		for i in range(0,num_punts+1):
			xi = -a/2 + a/2 * i / num_punts
			yi = b/2

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0
		
			for actuator in net.get_dynamixels():
				actuator.moving_speed = 50
				actuator.torque_enable = True
				actuator.torque_limit = 800 
				actuator.max_torque = 800
				actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			time.sleep(0.1)		


	if tros == 4:
		# Tram 4 - Diagonal
		num_punts = 15
		altura = -228
		for i in range(0,num_punts+1):
			xi = -a/2 + a/4 * i / num_punts
			yi = b/a * xi + 3*b/4

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
			    	actuator.moving_speed = 50
			    	actuator.torque_enable = True
			    	actuator.torque_limit = 800 
			    	actuator.max_torque = 800
			    	actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			time.sleep(0.2)

	
	if tros == 5:
		# Tram 5 - Corda
		num_punts = 5
		altura = -228
		for i in range(0,num_punts+1):
			xi = 0
			yi = b/2 - b/8 * i / num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
				actuator.moving_speed = 50
				actuator.torque_enable = True
				actuator.torque_limit = 800 
				actuator.max_torque = 800
				actuator.goal_position = th[j]   		
				j += 1

			
			net.synchronize()
			time.sleep(0.1)


	if tros == 6:
		# Tram 6 - Cap
		num_punts = 60
		altura = -228
		for i in range(1,num_punts+1):
			zita = -pi/2 - 2*pi * i /num_punts
			xi = 0 + b/8 * math.cos(zita)
			yi = b/4 + b/8 * math.sin(zita) 

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
				actuator.moving_speed = 30
				actuator.torque_enable = True
				actuator.torque_limit = 800 
				actuator.max_torque = 800
				actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			time.sleep(0.1)


	if tros == 7:
		# Tram 7 - Cos
		num_punts = 5
		altura = -228
		for i in range(0,num_punts+1):
			xi = 0
			yi = b/8 - 3*b/8 * i / num_punts

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0
		
			for actuator in net.get_dynamixels():
				actuator.moving_speed = 50
			    	actuator.torque_enable = True
			    	actuator.torque_limit = 800 
			    	actuator.max_torque = 800
			    	actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			time.sleep(0.3)


	if tros == 8:	
		# Tram 8 - Bracos
		num_punts = 10
		altura = -228
		for i in range(0,num_punts+1):
			xi = -a/4 + a/2 * i / num_punts
			yi = 0

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
			    	actuator.moving_speed = 50
			    	actuator.torque_enable = True
				actuator.torque_limit = 800 
			    	actuator.max_torque = 800
			    	actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			time.sleep(0.1)


	if tros == 9:		
		# Tram 9 - Cama 1
		num_punts = 5
		altura = -228
		for i in range(0,num_punts+1):
			xi = 0 - a/4 * i / num_punts
			yi = b/(2*a) * xi - b/4

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
			    	actuator.moving_speed = 50
			    	actuator.torque_enable = True
			    	actuator.torque_limit = 800 
				actuator.max_torque = 800
			    	actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			time.sleep(0.1)

	
	if tros == 10:		
		# Tram 10 - Cama 2
		num_punts = 5
		altura = -228
		for i in range(0,num_punts+1):
			xi = 0 + a/4 * i / num_punts
			yi = -b/(2*a) * xi - b/4

			th1,th2,th3 = angles(xi + centre[0], yi + centre[1], altura)
			th = [th1,th2,th3]
			j = 0

			for actuator in net.get_dynamixels():
			    	actuator.moving_speed = 50
			    	actuator.torque_enable = True
			    	actuator.torque_limit = 800 
			    	actuator.max_torque = 800
				actuator.goal_position = th[j]
				j += 1

			
			net.synchronize()
			time.sleep(0.1)


	# "Pujadeta"
	th1,th2,th3 = angles(pos_final[tros-1][0] + centre[0], pos_final[tros-1][1] + centre[1], -180)
	th = [th1,th2,th3]
	j = 0
		
	l_speed = [50,50,50,50,50,50,50,50,50,50]
	for actuator in net.get_dynamixels():
		actuator.moving_speed = l_speed[tros-1]
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	l_sleep = [1,1,1,1,1,1,1,1,1,1]
	time.sleep(l_sleep[tros-1])


	# Fi
	th1,th2,th3 = angles(0, 0, -150)
	th = [th1,th2,th3]
	j = 0
		
        for actuator in net.get_dynamixels():
            actuator.moving_speed = 100
            actuator.torque_enable = True
            actuator.torque_limit = 800 
            actuator.max_torque = 800
            actuator.goal_position = th[j]
	    j += 1

        net.synchronize()
	time.sleep(1)


# FUNCIONS QUE DIBUIXEN LES LINIES ON S'ESCRIUEN LES LLETRES ----------------------------
def una_linia(posicio, net):
	
	"""
	Dibuixa una linia en la posicio 'posicio', entre 1 i 7,
	de la lletra la paraula.
	"""	

	centre = l_centres[posicio - 1]

	# Posicio inicial
	th1,th2,th3 = angles(-a/2 + centre[0], -3*b/4 + centre[1], -200)
	th = [th1,th2,th3]
	j = 0
	
        for actuator in net.get_dynamixels():
		actuator.moving_speed = 100
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

	net.synchronize()
	l_sleep = [2,0.5,0.5,0.5,0.5,0.5,0.5]
	time.sleep(l_sleep[posicio-1])
	
	th1,th2,th3 = angles(-a/2 + centre[0], -3*b/4 + centre[1], -220)
	th = [th1,th2,th3]
	j = 0
		
	for actuator in net.get_dynamixels():
		actuator.moving_speed = 40
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800
		actuator.goal_position = th[j]
		j += 1

		
	net.synchronize()
	l_sleep = [1,0.5,0.5,0.5,0.5,0.5,0.5]
	time.sleep(l_sleep[posicio-1])
	
		
	# Tram 1 - Linia
	l_punts = [10,10,10,10,10,10,10]
	num_punts = l_punts[posicio-1]
	l_altures = [-227,-227,-227,-227,-227,-227,-227]
	for i in range(0,num_punts+1):
		xi = -a/2 + a * i / num_punts
		yi = -3*b/4

		th1,th2,th3 = angles(xi + centre[0], yi + centre[1], 						     l_altures[posicio-1])
		th = [th1,th2,th3]
		j = 0
	
		l_speed = [30,30,30,30,30,30,30]
		for actuator in net.get_dynamixels():
			actuator.moving_speed = l_speed[posicio-1]
			actuator.torque_enable = True
			actuator.torque_limit = 800 
			actuator.max_torque = 800
			actuator.goal_position = th[j]   		
			j += 1

			
		net.synchronize()
		l_sleep = [0.1,0.1,0.1,0.1,0.1,0.1,0.1]
		time.sleep(l_sleep[posicio-1])


	# "Pujadeta"
	time.sleep(0.4)
	th1,th2,th3 = angles(a/2 + centre[0], -b/2 + centre[1], -200)
	th = [th1,th2,th3]
	j = 0
		
        for actuator in net.get_dynamixels():
            actuator.moving_speed = 80
            actuator.torque_enable = True
            actuator.torque_limit = 800 
            actuator.max_torque = 800
            actuator.goal_position = th[j]
	    j += 1

        net.synchronize()
	time.sleep(0.5)


def linies(longitud, net):
	
	"""
	Dibuixa totes les linies necessaries per a una paraula de longitud 'longitud'
	"""

	for pos in range(1,longitud+1):
		una_linia(pos, net)

	punt(0,0,-150,100,net)

