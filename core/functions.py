import os
import time
import sys
import subprocess
from scapy.all import get_if_addr, get_if_hwaddr, get_working_if
from termcolor import colored
import re
import inspect



############# Banner #############
def banner():
	# Info about program --> Display to the user
	print colored("  .;'                     `;,    ",'green')
	print colored(" .;'  ,;'             `;,  `;,   ",'green'),
	print colored("Advanced WiFi Jammer",'white',attrs=['bold','underline'])
	print colored(".;'  ,;'  ,;'     `;,  `;,  `;,  ",'green')
	print colored("::   ::   :  ",'green'),
	print colored("(_) ",'green',attrs=['blink']),
	print colored(" :   ::   ::  ",'green'),
	print colored("Automated Wireless Signal Jammer",'white')
	print colored("':.  ':.  ':.",'green'),
	print colored("/_\\",'green',attrs=['blink']),
	print colored(",:'  ,:'  ,:'  ",'green')
	print colored(" ':.  ':.   ",'green'),
	print colored("/___\\",'green',attrs=['blink']),
	print colored("  .:'  ..:'   ",'green'),
	print colored("Designed For Linux",'white')
	print colored("  ':.      ",'green'),
	print colored("/_____\\ ",'green',attrs=['blink']),
	print colored("    ,:'     ",'green'),
	print colored("https://github.com/zflemingg1/WiFi-Jammer",'white')
	print colored("           /       \\",'green',attrs=['blink'])
	print colored (30 * "-", 'cyan')




############# Network Functions #############

def check_conflicting_processes():
	conflicting_processes = os.popen("airmon-ng check").read()
	pid_pnames = []
	pid_pname_re = re.compile(r'^\s*(\d+)\s*([a-zA-Z0-9_\-]+)\s*$')
	for line in conflicting_processes.split('\n'):
		match = pid_pname_re.match(line)
		if match:
			pid = match.group(1)
			pname = match.group(2)
			pid_pnames.append((pid, pname))
	return pid_pnames
	
def change_wireless_channel(number,interface):
	print "Changing to channel " + number
	try:
		#os.system("iwconfig " + interface + " channel " + number)
		change = subprocess.Popen("iwconfig " + interface + " channel " + number, shell=True).wait()
		#change.kill()
		print "sleeping in try"
	except Exception as e:
		print str(e)
		print "sleeping in except"

def get_list_of_interfaces():
	# Add Wireless Interfaces to list
	FNULL = open(os.devnull, 'w')
	proc = subprocess.Popen(['iwconfig'],stdout=subprocess.PIPE, stderr=FNULL)
	iface = ''
	interfaces = []
	
	# For loop o iterate over interfaces and add wireless ones to list
	for line in proc.communicate()[0].split('\n'):
		
		if line.startswith((' ', '\t')) or len(line) ==0:  # Ignore if line starts with a space or is of 0 length
			continue
		else:
			iface = line[:line.find(' ')]  # is the interface
		
		interfaces.append(iface) # Add interface to list
		
	return interfaces

def get_ip_of_interface(interfaces_list):
	interfaces = {}
	for iface in interfaces_list:
		ip_address = get_if_addr(iface)
		if (ip_address == "0.0.0.0") or (ip_address is None):
			interfaces[iface] = "None"
		else:
			interfaces[iface] = ip_address
			
	return interfaces
		

def user_select_interface():
	system_clear()
	interfaces = get_list_of_interfaces()
	
	## Add Ip Addresses to list for number of interfaces ##
	interface_list = get_ip_of_interface(interfaces)

	i = 0
	count = 0
	banner()
	print colored ("Available Interfaces (Interface:IP Address)", 'yellow')
	for interface in interface_list:
		count +=1
		print(repr(count) + "." + ''.join([' : '.join([k,v]) for k, v in interface_list.items()]))
		i+=1

		## User Selects Interface ##
		choice = user_input_integer(count)
		selected_interface = interfaces[choice - 1]

		return selected_interface

def spoof_mac_address(interface):
	banner()
	print colored ("[*] Spoofing Mac Address For " + interface,'yellow')
	time.sleep(1)
	os.system("ifconfig " + interface + " down")
	mac_address_info = os.popen("macchanger -r " + interface).read()
	mac_address_info = mac_address_info[:-1]
	os.system("ifconfig " + interface + " up")
	print colored ("[*] Spoofing Mac Address For " + interface + " [OK]",'green')
	time.sleep(1)
	return mac_address_info 
	
	
def enable_monitor_mode(interface):
	print colored("\n[*] Enabling Monitor Mode On: " + interface,'yellow')
	time.sleep(1)
	try:
		os.system("ifconfig " + interface + " down")
		os.system("iwconfig " + interface + " mode monitor")
		os.system("ifconfig " + interface + " up")
		print colored("[*] Enabling Monitor Mode On: " + interface + " [OK]",'green')
		time.sleep(1)
		system_clear()
	except Exception as e:
		print("[!!] Error unable to to set up monitoring mode on interface: " + interface)
		print str(e)
	
	
	
	
	
	# To Restore From Monitor Mode
	#print("[*] Enabling Monitor Mode On: " + interface)
	#os.system("ifconfig " + interface + "down")
	#os.system("iwconfig " + interface + " mode managed")
	#os.system("ifconfig " + interface + "up")
	#print("Monitor Mode Successfully Enabled On: " + interface)
	
	
	# To restore
	#print("Restoring Mac Address For " + interface)
	#os.system("ifconfig " + interface + " down")
	#os.system("macchanger -p " + interface)
	#os.system("ifconfig " + interface + " up")
	
	 



############# System Functions #############

def cleanup(interface,interface_status,mac_address_spoofed,restart_services): # If User Chooses To Exit The Program
	# If no interface has been selected
	if interface_status == False and len(restart_services) == 0:
		print colored("\nUser Terminated Program\n",'red',attrs=['bold'])
		exit(0)
	else:
		system_clear()
		banner()
		print colored("\n[*] Terminating Program...\n",'red',attrs=['bold'])
		#print inspect.stack()[1][3]
		# Restore Mac Address
		if mac_address_spoofed == True:
			print colored("[*] Restoring Mac Address For " + interface,'yellow',attrs=['bold'])
			os.system("ifconfig " + interface + " down")
			os.system("macchanger -p " + interface)
			os.system("ifconfig " + interface + " up")
			print colored("[*] Restoring Mac Address For " + interface + " [OK]\n",'green',attrs=['bold'])
		
		# Restore Managed Mode From Monitor
		if interface_status == True:
			print colored("[*] Disabling Monitor Mode & Restoring Managed Mode For " + interface,'yellow',attrs=['bold'])
			os.system("ifconfig " + interface + " down")
			os.system("iwconfig " + interface + " mode managed")
			os.system("ifconfig " + interface + " up")
			print colored("[*] Disabling Monitor Mode & Restoring Managed Mode For " + interface + " [OK]\n",'green',attrs=['bold'])
		
		# Restart Network Services
		if restart_services:
			# remove dhclient from service list -> unnecessary
			count = 0
			for element in restart_services:
				if "dhclient" in element:
					restart_services.pop(count)
				count +=1
				
			for element in restart_services:
				print colored("[*] Restarting Service " + element[1],'yellow')
				try:
					os.system("service " + element[1] + " restart")
					print colored("[*] Restarting Service " + element[1] + " [OK]\n",'yellow')
				except Exception as e:
					print e
					
		# now exit the program
		exit(0)
			
def terminate_conflicting_processes(conflicting_processes):
	print colored("\nDo you wish to terminate these services? (Note: Services will restart upon terminating program)",'yellow')
	print colored("1. Yes",'cyan')
	print colored("2. No",'cyan')
	choice = user_input_integer(2)
	
	if choice == 1:
		print colored("\n[*] Terminating Conflicting Services...",'yellow')
		for element in conflicting_processes:
			try:
				os.system("kill " + element[0])
			except Exception as e:
				print e
		print colored("[*] Terminating Conflicting Services... [OK]\n",'yellow')
		time.sleep(1)
		system_clear()
		banner()
		return (conflicting_processes,2)
	else:
		system_clear()
		banner()
		return ('',1)

def system_clear():
	os.system("clear")
	return


def user_input_integer(num_range):
	while True:
    		try:  
			userInput = int(raw_input('\nPlease Enter Choice [' + repr(1) + '-' + repr(num_range) + ']: '))       
    		except ValueError:
       			print("Not an integer! Try again.")
       			continue
    		else:
       			if(userInput < 1 or userInput > num_range ):
				print("Error Please Select A Valid Number")
			else:
				return userInput 
       				break 


def list_network_connections(interface):
	print("1.Get List of Targets On Network")

	## Get User Choice ##
	ip_range = get_ip_of_interface(interface)
	ip_range =  (".".join(ip_range.split('.')[0:-1]) + '.*') ## Format String to 0.0.0.*
	## Take action as per selected menu-option ##
	subprocess.Popen(["xterm -hold -e nmap -sS -O " + ip_range],shell=True)

	



	
			



