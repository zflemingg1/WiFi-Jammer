# Program to jam wifi by preventing clients from connecting to a target network
# Author: Zach Fleming

# Import the relevant python libraries
from termcolor import colored
from core import functions
from core import network_scanner
from tabulate import tabulate
import os
import time

class Main_Menu():
	
	interface_selected = False
	mac_address_spoofed = False
	monitor_mode = ''
	interface = ''
	conflicting_processes = []
	processes_terminated = 0
	
	# Initialize class
	def __init__(self):
		self.menu()
		
	def additional_banner_info(self):
		if len(self.conflicting_processes) == 0 and self.processes_terminated == 0:
			self.conflicting_processes = functions.check_conflicting_processes()
			
			if len(self.conflicting_processes) !=0:
				print colored("[!] Conflicting Processes Found...\n",'yellow',attrs=['bold'])
				print colored(tabulate(self.conflicting_processes, headers=['PID','Process']),'red',attrs=['bold'])
				
				# kill conflicting processes
				self.conflicting_processes, self.processes_terminated = functions.terminate_conflicting_processes(self.conflicting_processes)
			
			
			
		if self.monitor_mode != '':
			print colored(self.monitor_mode,'red')
				
		if self.mac_address_spoofed == True:
			print colored(self.mac_address_info,'magenta'),
			print colored(" [Spoofed]",'magenta', attrs=['bold'])
		
	def menu(self):
		
		while 1:
			try:
				functions.banner()
				self.additional_banner_info()
				print colored("\nPlease Select 1 Of The Following Options\n", 'yellow',attrs=['bold'])
				print("1. Select Wireless Interface")
				print("2. List Wireless Networks")
				print("3. Exit\n")
			
				choice = functions.user_input_integer(3)
				if choice == 1:
					self.interface = functions.user_select_interface()
					self.interface_selected = True
					functions.system_clear()
					self.mac_address_info = functions.spoof_mac_address(self.interface)
					self.mac_address_spoofed = True
					functions.enable_monitor_mode(self.interface)
					self.monitor_mode = ("Monitor Mode: " + "[" + self.interface + "]")
					
				
				elif choice == 2 and self.interface_selected is True:
					functions.system_clear()
					functions.banner()
					self.additional_banner_info()
					network_scanner.launch_network_discovery(self.interface,self.conflicting_processes)
					
				elif choice == 3:
					if self.processes_terminated == 0:
						self.conflicting_processes = [] # if user hasn't decided to chose whether to kill processes or not --> inital run
						
					functions.cleanup(self.interface,self.interface_selected,self.mac_address_spoofed,self.conflicting_processes)
					
				
				else:
					functions.system_clear()
					print colored ("[!!] An interface must be selected",'yellow',attrs=['bold'])
			except KeyboardInterrupt:
				if self.processes_terminated == 0:
					self.conflicting_processes = [] # if user hasn't decided to chose whether to kill processes or not --> inital run
	
				functions.cleanup(self.interface,self.interface_selected,self.mac_address_spoofed,self.conflicting_processes)
	
		
		
		
Main_Menu()
		
