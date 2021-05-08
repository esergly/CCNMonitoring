"""
    The tool-generator for CCN nodes monitoring report.
    Uses log-files of Mobaxterm terminal sessions as input and
    send report via e-mail as output actions.

"""
import sys
import os
import re
from os import listdir
from os.path import isfile, join
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime

FOLDER = r'C:\Users\***\Downloads\\'
CPU_MEM_KY, TPS_KY, CPU_KY, MEM_KY = [], [], [], []
CPU_MEM_LV, TPS_LV, CPU_LV, MEM_LV = [], [], [], []
ALARM_COUNTER_KY, ALARM_COUNTER_LV = 0, 0
# check if present and create list of source files
files = [f for f in listdir(FOLDER) if isfile(join(FOLDER, f))]
for _ in files:
    if _[-4:] == '.log':
        # start to separate and collect data from the source files
        with open(f'{FOLDER}{_}', 'r', encoding='utf-8') as file:
            for line in file:
                # number of requests per second
                if 'Voice-Charging-FirstInterrogation-Successful' in line:
                    if '.103.' in _:
                        TPS_KY.append(float(line[-10:].strip()) / 300)
                    elif '.99.' in _:
                        TPS_LV.append(float(line[-10:].strip()) / 300)
                elif re.match(r'^[S|P][C|L][-][\d]', line):
                    # counters value of PL and SC memory usage
                    if line[20] == '%':
                        if '.103.' in _:
                            CPU_MEM_KY.append(float(line[16:20].strip()))
                        elif '.99.' in _:
                            CPU_MEM_LV.append(float(line[16:20].strip()))
                    elif line[21] == '%':
                        if '.103.' in _:
                            CPU_MEM_KY.append(float(line[16:21].strip()))
                        elif '.99.' in _:
                            CPU_MEM_LV.append(float(line[16:21].strip()))
                elif 'activeSeverity=MAJOR' in line or 'activeSeverity=CRITICAL' in line:
                    # counters value of active alarms not elder then 24 hours
                    if '.103.' in _:
                        ALARM_COUNTER_KY += 1
                    elif '.99.' in _:
                        ALARM_COUNTER_LV += 1
                elif 'originalEventTime=' in line:
                    time_delta = datetime.datetime.strptime(
                        datetime.datetime.strftime(datetime.datetime.now(),
                                                   '%Y-%m-%dT%H:%M:%S'), '%Y-%m-%dT%H:%M:%S') \
                                 - datetime.datetime.strptime(line[-31:-12], '%Y-%m-%dT%H:%M:%S')
                    if time_delta.days > 0:
                        if '.103.' in _:
                            ALARM_COUNTER_KY -= 1
                        elif '.99.' in _:
                            ALARM_COUNTER_LV -= 1
ONE_TPS_KY = round(sum(TPS_KY) / 8)
TOTAL_TPS_KY = round(sum(TPS_KY))
ONE_TPS_LV = round(sum(TPS_LV) / 8)
TOTAL_TPS_LV = round(sum(TPS_LV))
for i in range(8):
    CPU_KY.append(CPU_MEM_KY[:12])
    MEM_KY.append(CPU_MEM_KY[12:24])
    CPU_MEM_KY[:] = CPU_MEM_KY[24:]
    CPU_LV.append(CPU_MEM_LV[:12])
    MEM_LV.append(CPU_MEM_LV[12:24])
    CPU_MEM_LV[:] = CPU_MEM_LV[24:]
AVR_CPU_KY = round((sum(sum(x) for x in CPU_KY)) / 96, 2)
AVR_MEM_KY = round((sum(sum(x) for x in MEM_KY)) / 96, 2)
AVR_CPU_LV = round((sum(sum(x) for x in CPU_LV)) / 96, 2)
AVR_MEM_LV = round((sum(sum(x) for x in MEM_LV)) / 96, 2)
# resulting report in console to check it before send via e-mail
print("DC1 CCN KYIV")
print(f'Current Throughput in one CCN, TPS                        {ONE_TPS_KY}')
print(f'Current Throughput in total CCN, TPS                      {TOTAL_TPS_KY}')
print(f'Major / Critical alarms for today                             {ALARM_COUNTER_KY}')
print(f'Average CPU utilization is currently standing, %    {AVR_CPU_KY}')
print(f'Average Memory consumption is now, %               {AVR_MEM_KY}')
print()
print("DC2 CCN LVIV")
print(f'Current Throughput in one CCN, TPS                        {ONE_TPS_LV}')
print(f'Current Throughput in total CCN, TPS                      {TOTAL_TPS_LV}')
print(f'Major / Critical alarms for today                             {ALARM_COUNTER_LV}')
print(f'Average CPU utilization is currently standing, %    {AVR_CPU_LV}')
print(f'Average Memory consumption is now, %               {AVR_MEM_LV}')

address_book = ['user1@mail.com',
                'user2@mail.com',
                'user3@mail.com',
                'user4@mail.com']
msg = MIMEMultipart()
SENDER = 'sender@mail.com'
subject = f'CCN node monitoring \
{datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y %H:%M")}'
# body = f'Current Throughput in one CCN, TPS                        {ONE_TPS}\n
# Current Throughput in total CCN,
# TPS   ' \ f'                     {TOTAL_TPS}\n
# Major / Critical alarms for todayMF
# NO\nAverage ' \ f' CPU utilization is currently standing, %     {AVR_CPU}\n
# Average Memory consumption is now, %               ' \ f'{AVR_MEM} '
BODY_HTML = """<html> <head> </head> <body> <p><strong><span style="font-size:18px">DC1 CCN KYIV
</span></strong></p><p><span style="font-size:16px"><span style="font-family:Arial,Helvetica,sans-serif"><em><span 
style="color:#1f497d">Current Throughput in one CCN, TPS&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; {ONE_TPS_KY}</span></em></span></span></p> <p><span style="font-size:16px"><span 
style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Current Throughput in total CCN, 
TPS&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
{TOTAL_TPS_KY}</span></em></span></span></p> <p style="text-align:justify"><span style="font-size:16px"><span 
style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Major / Critical alarms for 
today&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
&nbsp; &nbsp; {ALARM_COUNTER_KY}</span></em></span></span></p> <p><span style="font-size:16px"><span 
style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Average CPU utilization is currently 
standing, %&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;{AVR_CPU_KY}</span></em></span></span></p> <p><span 
style="font-size:16px"><span style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">
Average Memory consumption is now, %&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;{AVR_MEM_KY} 
</span></em></span></span></p> <p>&nbsp;</p> <p><strong><span style="font-size:18px">DC2&nbsp;CCN 
LVIV</span></strong></p> <p><span style="font-size:16px"><span style="font-family:Arial,Helvetica,
sans-serif"><em><span style="color:#1f497d">Current Throughput in one CCN, TPS&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; {ONE_TPS_LV}</span></em></span></span></p> <p><span 
style="font-size:16px"><span style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Current 
Throughput in total CCN, TPS&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
{TOTAL_TPS_LV}</span></em></span></span></p> <p style="text-align:justify"><span style="font-size:16px"><span 
style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Major / Critical alarms for 
today&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 
&nbsp; &nbsp; {ALARM_COUNTER_LV}</span></em></span></span></p> <p><span style="font-size:16px"><span 
style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Average CPU utilization is currently 
standing, %&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;{AVR_CPU_LV}</span></em></span></span></p> <p><span 
style="font-size:16px"><span style="font-family:Arial,Helvetica,sans-serif"><em><span style="color:#1f497d">Average 
Memory consumption is now, %&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;{AVR_MEM_LV} 
</span></em></span></span></p> <p><br /> <img src="cid:image1" /></p> <p>&nbsp;</p> </body> </html>""" \
    .format(**locals())
msg['From'] = SENDER
msg['To'] = ','.join(address_book)
msg['Subject'] = subject
# msg.attach(MIMEText(test_msg, 'plain'))
msg.attach(MIMEText(BODY_HTML, 'html'))
os.chdir(sys._MEIPASS)  # use it for pyinstaller to add an external file to exe package
# add picture with e-mail signature to the report-mail body
with open('sign.png', 'rb') as fp:
    msgImage = MIMEImage(fp.read())
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

s = smtplib.SMTP('email.smpt-server.net')
s.sendmail(SENDER, address_book, msg.as_string())
s.quit()
# clean the folder with the source files
for _ in files:
    if _[-4:] == '.log':
        try:
            os.remove(f'{FOLDER}{_}')
        except PermissionError:
            print("Next time before removing please close terminals connections to CCNs!")
