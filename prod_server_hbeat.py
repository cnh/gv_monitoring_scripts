#!/usr/bin/python


'''
This script requires Python 2.7 or greater, 
as it uses the subproces.check_output, which is availablen in Python >= 2.7

It is run using crotab, every 30 minutes, using the following entry in user backup01's crontab, 
on the machine 10.22.5.46, using crontab -e
 */30 * * * * cd /home/backup01/monitoring && localpy273/bin/python2.7 prod_server_hbeat.py 2>> /home/backup01/monitoring/cron_monitoring.log

Path to this script on 10.22.5.46
/home/backup01/monitoring/prod_server_hbeat.py

It logs it's output in (appends to the following file, after every 30 minutes) :
/home/backup01/monitoring/monitor.log

This script runs on 10.22.5.46, on the main production server inside the iit n/w, every 30 minutes.
    It performs 2 main tasks :
    1. It runs the command 'wanrouter status | grep Disconnected'
       If the above command returns 0, i.e. currently wanrouter is Disconnected,it sends an email to the admins
    2. It also runs the command 'wanrouter status | grep Connected'
       If wanrouter is neither connected or disconnected, it send an email to the admins
'''


import os
#import smtplib
import commands
import sys
#import httplib


#import send_email # to use the send_email(sub,body,to_list) function to send emails defined in send_email.py


from datetime import datetime

import subprocess
#import socket
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
		#login_string = 'ssh zahirk@106.187.101.30 python send_email.py'
		user = 'zahirk'
		remote_ip = '106.187.101.30'
		cmd = 'python send_email.py "%s" "%s"' % (sub, body)
		try:
			out = subprocess.check_output(['ssh', '%s@%s' % (user, remote_ip), cmd])
		except subprocess.CalledProcessError as e:
			monitor_logfile.write('\n'+ str(datetime.now())+' \n Error in sending email '+str(e) )
			print >>sys.stderr, str(e)   # handle/log the error, retry
	def get_ipadd_machinename():
		'''
		returns ip add. & hostname of machine where this monitoring script runs
		'''
		return {'ipadd':commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 
		'hostname':commands.getoutput("/bin/hostname") }
	cmd0 =  '/usr/sbin/wanrouter status'
	cmd1 = '/usr/sbin/wanrouter status | grep Disconnected'
	cmd2 = '/usr/sbin/wanrouter status | grep Connected'
	ipadd_machinename = get_ipadd_machinename()
	(status0, output0) = commands.getstatusoutput(cmd0)
	(status1, output1) = commands.getstatusoutput(cmd1)
	(status2, output2) = commands.getstatusoutput(cmd2)
	cmd_string = '\n\n' + str(datetime.now()) +'\n Output of \'wanrouter status\' is \n' 
	cmd_string += '************************************************************\n'
	cmd_string += output0 +'\n'
	cmd_string += '************************************************************ \n'
	print cmd_string
	monitor_logfile.write(cmd_string)
	cmd1_string = '\n\n' + str(datetime.now()) +'\n Output of \'' + cmd1  + '\' is \n' + output1
	cmd1_string += '\n\n Return status of \'' + cmd1 + '\' is ' + str(status1)
	print cmd1_string
	monitor_logfile.write(cmd1_string)
	cmd2_string = '\n\n' + str(datetime.now()) +'\n Output of \'' + cmd2  + '\' is \n' + output2
	cmd2_string += '\n\n Return status of \'' + cmd2 + '\' is ' + str(status2)
	print cmd2_string
	monitor_logfile.write(cmd2_string)
	#commands.getstatusoutput('wanrouter status | grep disconnected ')
	if(status1 == 0):
		e_sub = 'gv_diag_wan_router_disconnected at ' + str(datetime.now())
		e_body = '\n' + str(datetime.now()) +'\n wan router is disconnected'
		monitor_logfile.write(e_body)
		e_body += '\n' + str(datetime.now()) +' monitoring script ran on host named \'' + ipadd_machinename['hostname'] +  				   ' with ip add ' +   ipadd_machinename['ipadd']
		print e_body
		call_send_email(e_sub, e_body)
		sys.stderr.write(output1)
		sys.exit(1)
	elif(status1  and status2 ):
		e_sub1 = 'wanrouter has no status '  + str(datetime.now())
		e_body1 = '\n' + str(datetime.now()) +'\n wan router is neither connected/disconnected'
		monitor_logfile.write(e_body1)
		#e_body1 += '\n Output of wanrouter status was \n______________________________________________\n' + output0 + '________________________________________________\n'
		e_body1 += cmd_string
		e_body1 += '\n' + str(datetime.now()) +' monitoring script ran on host named \'' + ipadd_machinename['hostname'] +  				   ' \' with ip add ' +   ipadd_machinename['ipadd']
		#call_send_email(e_sub1, e_body1)
		print e_body1
		sys.stderr.write(output1)
		sys.stderr.write(output2)
		sys.exit(1)



finally: 
monitor_logfile.close()		
