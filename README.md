# WiFi-Jammer
Simple Python automated tool to jam all traffic for either selected clients or networks within range and disconnect them from their AP. Simple Menu Interface to automate the entire process. 

### Launching the program

To use the program simply open up a terminal navigate to the directory and run it with "python wifi-jammer.py"

### Running The Program
As soon as the program starts it checks for any processes that may interfere with it. You can then either select option 1 to kill these processes or option 2 to ignore. Note if you kill them, they will be restarted as soon as the program is terminated

![alt text](screenshots/1.png "Sample Output")

Next you select your wireless interface

![alt text](screenshots/2.png "Sample Output")

![alt text](screenshots/3.png "Sample Output")

The program will then take steps to spoof your mac adress as an anti forensics measure and enable monitor mode on your chosen interface

![alt text](screenshots/4.png "Sample Output")

THe user then chooses to scan for target networks

![alt text](screenshots/5.png "Sample Output")

![alt text](screenshots/6.png "Sample Output")

The user then chooses either to target a client or an entire network

![alt text](screenshots/7.png "Sample Output")

To exit the program the user just has to press Ctrl+C. This will terminate the program and run the clean up process. The clean up process will restart all terminated process in step one if any. It will then restore the interfaces original mac address and put the interface back in managed mode. 

![alt text](screenshots/8.png "Sample Output")

### Built With

* Python 2.7.14

### Authors

*** Zach Fleming --> zflemingg1@gmail.com


