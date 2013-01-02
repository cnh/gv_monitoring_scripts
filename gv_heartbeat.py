#!/usr/bin/python


'''
This script requires Python 2.7 or greater, 
as it uses the subproces.check_output, which is availablen in Python >= 2.7

It is run using crotab, every 30 minutes, using the following entry in /etc/crontab, on the machine 10.22.5.49
*/30 *  * * *   gramvaani cd ~/monitoring && ~/.localpython_273/bin/python2.7 gv_heartbeat_v3.py

Path to this script on 10.22.5.49
/home/gramvaani/monitoring/gv_heartbeat_v3.py

It logs it's output in (appends to the following file, after every 30 minutes) :
/home/gramvaani/monitoring/monitor.log

This script runs on 10.22.5.49, on a machine inside the iit n/w, every 30 minutes.
    It performs 2 main tasks :
    1. It pings 10.22.5.46 & checks if a response is received.
       If not, it sends an email to the admins
    2. This script opens an http connection to 10.22.4.30/vapp(
    opens http connection to 10.22.4.30, & requests the head element for url vapp/ ) & 
    checks the http response code.
    If it is other than 200 (OK), it send an email to the admins
'''

import os
#import smtplib
import commands
import httplib
import sys


#import send_email # to use the send_email(sub,body,to_list) function to send emails defined in send_email.py


from datetime import datetime

import subprocess
import socket
import commands # to determine ip address

#from email.mime.text import MIMEText

#def send_email(sub, body, to_list, from_email='gramvaani@gmail.com'):
#    	msg = MIMEText(body)
#		msg['Subject'] = sub
#		username = 'gramvaani'
#		password = 'junoongv'
#		server = smtplib.SMTP('smtp.gmail.com:587')
#		server.starttls()
#		server.login(username,password)  
#		from_email = 'gramvaani@gmail.com'
#		server.sendmail(from_email, to_list, msg.as_string())	

try:
	monitor_logfile = open('monitor.log', 'a')
except IOError:
	print "\n Error opening monitor log file"
else:	
	def call_send_email(sub, body):
		"""
		passes it's arguments( sub & body) to the send_email function on 
		the machine specified by remote_ip
		"""
		#login_string = 'ssh zahirk@106.187.101.30 python send_email.py email_subject email_body'
		user = 'zahirk'
		remote_ip = '106.187.101.30'
		cmd = 'python send_email.py "%s" "%s"' % (sub, body)
		before_ssh_msg = '\n' + str(datetime.now()) +' \n Trying to ssh to remote m/c w/ ip '+ remote_ip +' to send email '
		print before_ssh_msg
		monitor_logfile.write(before_ssh_msg)
		#monitor_logfile.write('\n' + str(datetime.now()) +'\n Trying to ssh to remote m/c ' + remote_ip + ' to send email')
		try:
			out = subprocess.check_output(['ssh', '%s@%s' % (user, remote_ip), cmd])
		except subprocess.CalledProcessError as e:
			monitor_logfile.write('\n'+ str(datetime.now())+' \n Error in ssh-ing to ' + remote_ip + ' to send email '+str(e) )
			print >>sys.stderr, str(e)   # handle/log the error, retry
		after_ssh_msg = '\n' + str(datetime.now()) +' \n successfully ssh-ed to remote m/c w/ ip ' +remote_ip + ' & sent email to admins'
		print after_ssh_msg
		monitor_logfile.write(after_ssh_msg)
		#monitor_logfile.write('\n' + str(datetime.now()) +' \n successfully ssh-ed to remote m/c & sent email to admins')
		
	def get_ipadd_machinename():
		'''
		returns ip add. & hostname of machine where this monitoring script runs
		'''
		return {'ipadd':commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 
		'hostname':commands.getoutput("/bin/hostname") }


	#dest_emails = ['ashish.makani@gmail.com', 'dineshkapoor27@gmail.com']	
	hostname = "10.22.5.46" #ip address of production server, whose n/w status we want to test with ping
	response = os.system("ping -c 1 " + hostname)
	ipadd_machinename = get_ipadd_machinename()
	if(response == 0):
		print ('\n'+ str(datetime.now())+' \n ping to server w/ ip '+ hostname +' SUCCESS \n')
		monitor_logfile.write('\n'+ str(datetime.now())+' \n ping to server w/ ip '+ hostname +' SUCCESS \n')
	else:
	  	print (str(datetime.now()) + '\n ping to server w/ ip '+ hostname +' FAILED')
	  	#send_email.send_email('ping to server w/ ip '+hostname+ ' FAILED', 'str(datetime.now()) \n ping to'+ hostname +' #FAILED', dest_emails)
	  	e_sub = 'ping to server w/ ip '+hostname+ ' FAILED at ' + str(datetime.now()) 
	  	e_body = str(datetime.now()) + '\n ping to server w/ ip '+ hostname +' FAILED'
	  	e_body += '\n \n monitoring script ran on host named \'' + ipadd_machinename['hostname'] + ' with ip add ' +  \
			  ipadd_machinename['ipadd']
		print e_body
		monitor_logfile.write(e_body)
	  	call_send_email(e_sub, e_body)
	  	#os.system("ssh zahirk@106.187.101.30 python send_email.py ")
	  	#ssh_string = login_string + '\''+ str(e_sub) + '\' \'' + str(e_body) + '\''
	  	#ssh_status = os.system("ssh zahirk@106.187.101.30 python send_email.py \'" + str(e_sub) + "\' \'"+str(e_body) +"\'")
	  	#if ssh_status:
	  	#	monitor_logfile.write('\n ssh to remote email server FAILED')	  		
	  	# expands to "python send_email.py 'ping to server w/ ip 10.22.5.46 FAILED' '2012-09-17 18:29:42.818401 \n ping to server w/ ip 10.22.5.46 FAILED'"
		monitor_logfile.write('\n'+ str(datetime.now())+' \n ping to server w/ ip '+ hostname + 
		'FAILED, sent email to monitor admin \n')			
	#gv_webname = 'voice.gramvaani.org'
	gv_webname = '10.22.4.30'
	url = '/vapp/'
	try:
		print('\n Trying to open a connection to '+ gv_webname)
		monitor_logfile.write('\n' + str(datetime.now()) +' \n Trying to open http connection to '+ gv_webname)
		
		c = httplib.HTTPConnection(gv_webname, timeout = 60) 
		
		print('\n' + str(datetime.now()) +' \n Trying to fetch url '+ url +' on host '+ gv_webname)
		monitor_logfile.write('\n' + str(datetime.now()) +' \n Trying to fetch url '+ url +' on host '+ gv_webname)
		
		http_fetch_msg ='\n' + str(datetime.now()) +' \n Trying to get status & HTTP response code for the HEAD element, for url '\
				+ url +' on host ' +gv_webname
		monitor_logfile.write(http_fetch_msg)
		print http_fetch_msg
		#print('\n' + str(datetime.now()) +' \n Trying to get status & HTTP response code for the HEAD element')
					
		c.request ("HEAD", url)
		http_response_code = c.getresponse().status

	except Exception as e:
		#monitor_logfile.write('\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url)
		#print('\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url + '\n Error is ' +str(e))
		esub = '\n' + str(datetime.now()) +' \n Error opening http connection to '+ gv_webname+url
		ebody = '\n' + str(datetime.now()) + '\n Error opening http connection to '+ gv_webname+url + ' from machine \'' +    				ipadd_machinename['hostname'] +'\' with ip add ' +   ipadd_machinename['ipadd']+'\n Error is ' +str(e)
		print ebody
		monitor_logfile.write(ebody)
		call_send_email(esub, ebody)
		monitor_logfile.write('\n' + str(datetime.now()) +'\n Sent email to admins, as there was an error opening an http connection to '+ gv_webname+url )
		print('\n' + str(datetime.now()) +'\n Sent email to admins & logged that, there was an error opening an http connection to '+gv_webname+url )
		exit_msg = '\n' + str(datetime.now()) + 'Exiting now'
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
		call_send_email(e_sub1, e_body1)
		#os.system("ssh zahirk@106.187.101.30 python send_email.py \'" + str(e_sub) + "\' \'"+str(e_body) +"\'" )
		
		monitor_logfile.write('\n'+ str(datetime.now())+' \n http connection to '+ gv_webname+url+\
		 '\n FAILED with status ' + str(http_response_code) + '\n')
		print('\n'+ str(datetime.now())+' \n http connection to '+ gv_webname+url+\
		 '\n FAILED with status ' + str(http_response_code) + '\n')
	 
	 
	 #process = subprocess.Popen(['ssh','zahirk@10.76.9.4'], shell=False, )
	#make sure we eventually close the monitor log file
finally: 
	monitor_logfile.close()		
