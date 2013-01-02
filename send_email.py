#!/usr/bin/python


'''
   This script runs on the linode server, with ip 106.187.101.30,  outside
    the iit n/w, every 30 minutes.
    
    It is run using crotab, every 30 minutes, 
    using the following entry in /etc/crontab, on the machine 106.187.101.30,
    */30 *  * * *   zahirk  cd ~ && python send_email.py
    
    Path to this script on 106.187.101.30
    /home/zahirk/send_email.py
    
    It logs it's output in (appends to the following file, after every 30 minutes) :
    /home/zahirk/monitoring/monitor.log
    
    It performs 3 main tasks
    1. Other monitoring scripts, running inside the iit n/w, ssh to this
    machine & call the send_email function in this script to send email, in
    case of an abnomral event.
    This script is invoked by other scripts using python's subprocess.check_output, with the following string
    'ssh zahirk@106.187.101.30 python send_email.py email_subject email_body'
    
    2. The list of email addresses of admins, to whom, monitoring emails are sent, is defined in this script,
    in the variable 'admins'.
    3. This script opens an http connection to voice.gramvaani.org/vapp(
    opens http connection to voice.gramvaani.org
    & requests the head element for url vapp/ ) & checks the http response
    code.
    If it is other than 200 (OK), it send an email to the admins

'''


import smtplib
import sys
import os
from email.mime.text import MIMEText
import commands
import httplib
from datetime import datetime
import urllib


admins = ['ashish.makani@gmail.com', 'dineshkapoor27@gmail.com','zahir.koradia@gmail.com','jainarohit@gmail.com','er.kapildadheech@gmail.com','aaditeshwar@gmail.com']  
testing = ['ashish.makani@gmail.com']

#os.system("ssh zahirk@106.187.101.30 python send_email.py test_sub test_body ashish.makani@gmail.com")

for arg in sys.argv:
	print arg



def send_email(sub, body, to_list=admins, from_email='gramvaani@gmail.com'):
	msg = MIMEText(body)
	msg['Subject'] = sub
	username = 'gramvaani'
	password = 'junoongv'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)  
	from_email = 'gramvaani@gmail.com'
	server.sendmail(from_email, to_list, msg.as_string())
	print 'sent email successfully to ' + str(to_list)	

def send_email2(sub, body, to_list=testing, from_email='gramvaani@gmail.com'):
	msg = MIMEText(body)
	msg['Subject'] = sub
	username = 'gramvaani'
	password = 'junoongv'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)  
	from_email = 'gramvaani@gmail.com'
	server.sendmail(from_email, to_list, msg.as_string())
	print 'sent email successfully to ' + str(to_list)	

	
if __name__ == "__main__":
	if(len(sys.argv) >= 3):
		send_email(sys.argv[1], sys.argv[2])
	#else:
		#pass


try:
	os.chdir('monitoring') # change to the 'monitoring' directory so that the log file 'monitor.log' gets created there
	filename = str(datetime.date.today()) + '_monitor.log'
	#monitor_logfile = open(filename, 'a')
	monitor_logfile = open('monitor.log', 'a')
except IOError:
	print "\n Error opening monitor log file"
else:	
		
	def get_ipadd_machinename():
		'''
		returns ip add. & hostname of machine where this monitoring script runs
		'''
		return {'ipadd':commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 
		'hostname':commands.getoutput("/bin/hostname") }


	gv_webname = 'voice.gramvaani.org'
	#gv_webname = '10.22.4.30'
	url = '/vapp/'
	try:
		print('\n Trying to open a connection to '+ gv_webname)
		monitor_logfile.write('\n' + str(datetime.now()) +' \n Trying to open http connection to '+ gv_webname)
		
		c = httplib.HTTPConnection(gv_webname, timeout = 30) 
		
		msg2 = '\n' + str(datetime.now()) +' \n Making a request() call for the HEAD element & get the status code of the response'
		print msg2
		monitor_logfile.write(msg2)
					
		c.request ("HEAD", url)
		http_response_code = c.getresponse().status

		gv_url = 'http://voice.gramvaani.org/vapp/'
		#http_response_code = urllib.urlopen("http://voice.gramvaani.org/vapp/").getcode()
		#http_response_code = urllib.urlopen(gv_url).getcode()

	except Exception as e:
		#monitor_logfile.write('\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url)
		#print('\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url + '\n Error is ' +str(e))
		esub = '\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url
		ebody = '\n' + str(datetime.now()) + '\n Error opening http connection to '+ gv_webname+url + ' from machine \'' +    				ipadd_machinename['hostname'] +'\' with ip add ' +   ipadd_machinename['ipadd']+'\n Error is ' +str(e)
		print ebody
		monitor_logfile.write(ebody)
		send_email(esub, ebody)
		monitor_logfile.write('\n' + str(datetime.now()) +'\n Sent email to admins, as there was an error opening an http connection to '+ gv_webname+url )
		print('\n' + str(datetime.now()) +'\n Sent email to admins & logged that, there was an error opening an http connection to '+gv_webname+url )
		exit_msg = '\n' + str(datetime.now()) +'Exiting now'
		print exit_msg
		monitor_logfile.write(exit_msg)
		sys.exit(1)
	print http_response_code # should print 200 if everything is FINE
	if(http_response_code == 200):
		success_msg = '\n' + str(datetime.now()) +' \n Successfully opened http connection & got HTTP response for the HEAD ' + \
		 'element of  '+ gv_webname+url+ ' \n response code was ' + str(http_response_code) + ' ; SUCCESS \n'
		print (success_msg)
		monitor_logfile.write(success_msg)
		#print('\n' + str(datetime.now()) +' \n opening http connection to '+ gv_webname+url+ \
		#' \n response code was ' + str(http_response_code) + ' ; SUCCESS \n')
	else:
		#send_email.send_email('http to v.gv.org/vapp/ failed', 'str(datetime.now()) \n http connection to '+ gv_webname+url+ 			'\n FAILED with status ' + str(http_response_code), dest_emails)
		
		e_sub1 = ' http connection to '+ gv_webname+url+ ' FAILED '
		e_body1 = ' http connection to '+ gv_webname+url+ '\n FAILED with status ' + str(http_response_code)
		e_body1 += '\n' + str(datetime.now()) +' monitoring script ran on host named \'' + ipadd_machinename['hostname'] +  				   ' with ip add ' +   ipadd_machinename['ipadd']
		send_email(e_sub1, e_body1)
		#os.system("ssh zahirk@106.187.101.30 python send_email.py \'" + str(e_sub) + "\' \'"+str(e_body) +"\'" )
		
		monitor_logfile.write('\n'+ str(datetime.now())+' \n http connection to '+ gv_webname+url+\
		 '\n FAILED with status ' + str(http_response_code) + '\n')
		print('\n'+ str(datetime.now())+' \n http connection to '+ gv_webname+url+\
		 '\n FAILED with status ' + str(http_response_code) + '\n')
	 
	 
	 #process = subprocess.Popen(['ssh','zahirk@10.76.9.4'], shell=False, )
	#make sure we eventually close the monitor log file
finally: 
	monitor_logfile.close()		
