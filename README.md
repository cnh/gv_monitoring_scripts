gv_monitoring_scripts
=====================
Monitoring Scripts

There are 3 main monitoring related scripts :
1. send_email.py running on linode server, 106.187.101.30, outside the iit network
2. gv_heartbeat.py running on 10.22.5.49, inside the iit n/w.
3. prod_server_heartbeat.py running on the production machine, 10.22.5.46
These 3 scripts are checked into the git server, 10.76.9.6, in the branch call_stats, under VoiceDjango/scripts.
Descriptions of the above 3 scripts :
1. This script runs on the linode server, with ip 106.187.101.30, outside the iit n/w, every 30 minutes.
It is run using crotab, every 30 minutes, using the following entry in /etc/crontab, on the machine 106.187.101.30,
   */30 *  * * *   zahirk  cd ~ && python send_email.py
   
Path to this script on 106.187.101.30
   /home/zahirk/send_email.py
   
It logs it's output in (appends to the following file, after every 30 minutes) :
   /home/zahirk/monitoring/yyyy-mm-dd_monitor.log
   
It performs 3 main tasks :
   a. Other monitoring scripts, running inside the iit n/w, ssh to this
   machine & call the send_email function in this script to send email, in
   case of an abnomral event.
   This script is invoked by other scripts using python's subprocess.check_output, with the following string
   'ssh zahirk@106.187.101.30 python http_test.py email_subject email_body'
   
   b. The list of email addresses of admins, to whom, monitoring emails are sent, is defined in this script,
   in the variable 'admins'.
   c. This script opens an http connection to voice.gramvaani.org/vapp(
   opens http connection to voice.gramvaani.org
   & requests the head element for url vapp/ ) & checks the http response
   code.
   If it is other than 200 (OK), it send an email to the admins

2. This script requires Python 2.7 or greater, as it uses the subproces.check_output, which is available in Python >= 2.7
We therefore use a local install of Python2.7 & we use the python2.7 binary to execute this script using cron.
It is run using crotab, every 30 minutes, using the following entry in /etc/crontab, on the machine 10.22.5.49
     */30 *  * * *   gramvaani cd ~/monitoring && ~/.localpython_273/bin/python2.7 gv_heartbeat_v3.py
Path to this script on 10.22.5.49
   /home/gramvaani/monitoring/gv_heartbeat_v3.py
It logs it's output in (appends to the following file, after every 30 minutes) :
   /home/gramvaani/monitoring/monitor.log
This script runs on 10.22.5.49, on a machine inside the iit n/w, every 30 minutes.
   It performs 2 main tasks :
   a. It pings 10.22.5.46 & checks if a response is received.
      If not, it sends an email to the admins
   b. This script opens an http connection to 10.22.4.30/vapp(
   opens http connection to 10.22.4.30, & requests the head element for url vapp/ ) & 
   checks the http response code.
   If it is other than 200 (OK), it send an email to the admins

3. This script requires Python 2.7 or greater, as it uses the subproces.check_output, which is availablen in Python >= 2.7
We therefore use a local install of Python2.7 & we use the python2.7 binary to execute this script using cron.
It is run using crotab, every 30 minutes, using the following entry in user backup01's crontab, on the machine 10.22.5.46, using crontab -e
*/30 * * * * cd /home/backup01/monitoring && localpy273/bin/python2.7 prod_server_hbeat.py 2>> /home/backup01/monitoring/cron_monitoring.log
Path to this script on 10.22.5.46
/home/backup01/monitoring/prod_server_hbeat.py
It logs it's output in (appends to the following file, after every 30 minutes) :
/home/backup01/monitoring/monitor.log
This script runs on 10.22.5.46, on the main production server inside the iit n/w, every 30 minutes.
   It performs 2 main tasks :
   a. It runs the command 'wanrouter status | grep Disconnected'
      If the above command returns 0, i.e. currently wanrouter is Disconnected,it sends an email to the admins
   b. It also runs the command 'wanrouter status | grep Connected'
      If wanrouter is neither connected or disconnected, it send an email to the admins
