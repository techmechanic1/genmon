#!/usr/bin/env python
#-------------------------------------------------------------------------------
#    FILE: genpushover.py
# PURPOSE: genpushover.py sends Push notifications to Android, iOS and Desktop
#
#  AUTHOR: Stephen Bader - Stole a lot of code from gensms.py
#    DATE: 09-09-2017
#
# MODIFICATIONS:
#-------------------------------------------------------------------------------

import datetime, time, sys, signal, os, threading, socket
import atexit, getopt

try:
    from genmonlib.mylog import SetupLogger
    from genmonlib.mynotify import GenNotify
    from genmonlib.myconfig import MyConfig
    from genmonlib.mysupport import MySupport
    from genmonlib.mymsgqueue import MyMsgQueue
    from genmonlib.program_defaults import ProgramDefaults
except Exception as e1:
    print("\n\nThis program requires the modules located in the genmonlib directory in the github repository.\n")
    print("Please see the project documentation at https://github.com/jgyates/genmon.\n")
    print("Error: " + str(e1))
    sys.exit(2)

try:
    from chump import Application
except Exception as e1:
    print("\n\nThis program requires the chump module to be installed.\n")
    print("Please see the project documentation at https://github.com/jgyates/genmon.\n")
    print("Error: " + str(e1))
    sys.exit(2)


#---------------------GetErrorLine----------------------------------------------
def GetErrorLine():

    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lineno = exc_tb.tb_lineno
        return fname + ":" + str(lineno)
    except Exception as e1:
        return "Unknown Line " + str(e1)


#----------  Signal Handler ----------------------------------------------------
def signal_handler(signal, frame):

    try:
        GenNotify.Close()
        Queue.Close()
    except Exception as e1:
        log.error("signal_handler: " + str(e1))
    sys.exit(0)

#----------  OnRun -------------------------------------------------------------
def OnRun(Active):

    if Active:
        console.info("Generator Running")
        Queue.SendMessage("Generator Running")
    else:
        console.info("Generator Running End")

#----------  OnRunManual -------------------------------------------------------
def OnRunManual(Active):

    if Active:
        console.info("Generator Running in Manual Mode")
        Queue.SendMessage("Generator Running in Manual Mode")
    else:
        console.info("Generator Running in Manual Mode End")

#----------  OnExercise --------------------------------------------------------
def OnExercise(Active):

    if Active:
        console.info("Generator Exercising")
        Queue.SendMessage("Generator Exercising")
    else:
        console.info("Generator Exercising End")

#----------  OnReady -----------------------------------------------------------
def OnReady(Active):

    if Active:
        console.info("Generator Ready")
        Queue.SendMessage("Generator Ready")
    else:
        console.info("Generator Ready End")

#----------  OnOff -------------------------------------------------------------
def OnOff(Active):

    if Active:
        console.info("Generator Off")
        Queue.SendMessage("Generator Off")
    else:
        console.info("Generator Off End")

#----------  OnManual ----------------------------------------------------------
def OnManual(Active):

    if Active:
        console.info("Generator Manual")
        Queue.SendMessage("Generator Manual")
    else:
        console.info("Generator Manual End")

#----------  OnAlarm -----------------------------------------------------------
def OnAlarm(Active):

    if Active:
        console.info("Generator Alarm")
        Queue.SendMessage("Generator Alarm")
    else:
        console.info("Generator Alarm End")

#----------  OnService ---------------------------------------------------------
def OnService(Active):

    if Active:
        console.info("Generator Service Due")
        Queue.SendMessage("Generator Service Due")
    else:
        console.info("Generator Servcie Due End")

#----------  OnUtilityChange ---------------------------------------------------
def OnUtilityChange(Active):

    if Active:
        console.info("Utility Service is Down")
        Queue.SendMessage("Utility Service is Down")
    else:
        Queue.SendMessage("Utility Service is Up")
        console.info("Utility Service is Up")

#----------  OnSoftwareUpdate --------------------------------------------------
def OnSoftwareUpdate(Active):

    if Active:
        console.info("Software Update Available")
        Queue.SendMessage("Software Update Available")
    else:
        Queue.SendMessage("Software Is Up To Date")
        console.info("Software Is Up To Date")

#----------  OnSystemHealth ----------------------------------------------------
def OnSystemHealth(Notice):
    Queue.SendMessage("System Health : " + Notice)
    console.info("System Health : " + Notice)

#----------  OnFuelState -------------------------------------------------------
def OnFuelState(Active):
    if Active: # True is OK
        console.info("Fuel Level is OK")
        Queue.SendMessage("Fuel Level is OK")
    else:  # False = Low
        Queue.SendMessage("Fuel Level is Low")
        console.info("Fuel Level is Low")

#----------  SendNotice --------------------------------------------------------
def SendNotice(Message):

    try:
        app = Application(appid)

        if not app.is_authenticated:
            self.LogError("Unable to authenticate app ID")
            return False

        user = app.get_user(userid)

        if not user.is_authenticated:
            self.LogError("Unable to authenticate user ID")
            return False

        message = user.create_message(
            message = Message,
            sound = pushsound)

        message.send()

        console.info(message.id)
        return True
    except Exception as e1:
        log.error("Send Notice Error: " + GetErrorLine() + ": " + str(e1))
        console.error("Send Notice Error: " + str(e1))
        return False

#------------------- Command-line interface for gengpio ------------------------
if __name__=='__main__':

    console, ConfigFilePath, address, port, loglocation, log = MySupport.SetupAddOnProgram("genpushover")

    # Set the signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:

        config = MyConfig(filename = os.path.join(ConfigFilePath, 'genpushover.conf'), section = 'genpushover', log = log)

        appid = config.ReadValue('appid', default = None)
        userid = config.ReadValue('userid', default = None)
        pushsound = config.ReadValue('pushsound', default = 'updown')

        if appid == None or not len(appid):
            log.error("Error:  invalid app ID")
            console.error("Error:  invalid app ID")
            sys.exit(2)

        if userid == None or not len(userid):
            log.error("Error:  invalid user ID")
            console.error("Error:  invalid user ID")
            sys.exit(2)

    except Exception as e1:
        log.error("Error reading " +  os.path.join(ConfigFilePath, 'genpushover.conf') +": " + str(e1))
        console.error("Error reading " +  os.path.join(ConfigFilePath, 'genpushover.conf') +": " + str(e1))
        sys.exit(1)
    try:

        Queue = MyMsgQueue(config = config, log = log, callback = SendNotice)

        GenNotify = GenNotify(
                                        host = address,
                                        port = port,
                                        onready = OnReady,
                                        onexercise = OnExercise,
                                        onrun = OnRun,
                                        onrunmanual = OnRunManual,
                                        onalarm = OnAlarm,
                                        onservice = OnService,
                                        onoff = OnOff,
                                        onmanual = OnManual,
                                        onutilitychange = OnUtilityChange,
                                        onsoftwareupdate = OnSoftwareUpdate,
                                        onsystemhealth = OnSystemHealth,
                                        onfuelstate = OnFuelState,
                                        log = log,
                                        loglocation = loglocation,
                                        console = console,
                                        config = config)

        while True:
            time.sleep(1)

    except Exception as e1:
        log.error("Error: " + GetErrorLine() + ": " + str(e1))
        console.error ("Error: " + str(e1))
