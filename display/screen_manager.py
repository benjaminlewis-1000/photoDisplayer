#! /usr/bin/env python

import subprocess
import shlex
import re
import thread
import Queue
import sys
import termios
import pexpect
import threading
from time import sleep
import time
import os

class tvStateManager():

    def __init__(self):
      
      self.process = pexpect.spawn('cec-client')
      
      self.commandQueue = Queue.Queue()
      self.cecQueue = Queue.Queue()
      self.powerQueue = Queue.Queue()
      self.activeQueue = Queue.Queue()
      
      # self.powerQueue.put('unknown')
      # self.activeQueue.put('unknown')
      self.dir_path = os.path.dirname(os.path.realpath(__file__))
      # self.safeToDetermineState = False
      
      self.desiredState = 'off'

      self.stateSafeSemaphore = threading.Lock()
      
      self.powerSemaphore = threading.Lock()
      self.stateSemaphore = threading.Lock()
      self.powerDesiredSemaphore = threading.Lock()
      self.powerState = 'off'
      self.activeState = 'unknown'
      self.desiredPowerState = 'unknown'
      
      thread.start_new_thread(self.__tv_state_monitor__, () )
      thread.start_new_thread(self.__command_reader__, (self.process,) )
      thread.start_new_thread(self.__cec_output_consumer__, (self.process,) )
      # self.__determine_unknown_state__()
      
      
    def __determine_unknown_state__(self):
        sleep(5)
  
        powerState = self.__getPowerState__()
        activeState = self.__getActiveState__()
        
        # Sleep 10 seconds if necessary
        if computerState == 'raspi' or computerState == 'not_raspi':
            return # We have our answer 
        if powerState == 'on' or powerState == 'unknown': 
            # Don't want to mess with currently powered on TV - either it's
            # on the right input already or we don't want to hijack the TV from someone. 
            threading.Timer(5, self.__determine_unknown_state__).start()
        else: # Power is off
            if powerState == 'off':
                imgname = os.path.join(self.dir_path, 'dontpanic.png')
                imshow = subprocess.Popen(['/usr/local/bin/feh', '-ZxF', imgname]) 
                self.commandQueue.put('turnOn')
                self.process.sendline('as') 
                sleep(1)
                self.process.sendline('as')
    
                safeState = False
                #while not safeState:
                #    sleep(2)
                #    self.stateSafeSemaphore.acquire()
                #    safeState = self.safeToDetermineState 
                #    self.stateSafeSemaphore.release()
    
                self.stateSemaphore.acquire()
                activeState = self.activeState
                self.stateSemaphore.release()
                if computerState == 'raspi' :
                  print "Computer state is known as raspi - turning off screen"
                  self.turnOffScreen()
    
                if computerState == 'raspi' or computerState == 'not_raspi':
                  imshow.terminate()
                  return
                else:
                  print "Try, try again"
                  print "Computer state is {}, power state is {}".format(computerState, powerState)
                  # Try, try again
                  threading.Timer(5, self.__determine_unknown_state__).start()
                
            else:  # Shoot, someone turned the TV back on. Try again later. 
                # Try, try again
                threading.Timer(5, self.__determine_unknown_state__).start()
                  
    def __cec_output_consumer__(self, process):
      # This thread will block, but that's OK because the only thing it does is 
      # consume and put on the queue
      while 1:
        try:
            stdout = self.process.readline()
            stdout = stdout.lower().rstrip()
            self.cecQueue.put(stdout)
            #print stdout 
        except pexpect.exceptions.TIMEOUT:
            pass
    
    def __command_reader__(self, process):
      # Only reads off data from the cec process, since it will block if there
      # is no new data
      # desiredPowerState = 'off'
      while 1:
        
        sleep(1.5)

        # Workaround to check if the queue is empty - see if there is
        # something to read with a nonblocking call   
              
        powerState = self.__getPowerState__()
        activeState = self.__getActiveState__()
        desiredState = self.__getDesiredPowerState__()
        
        if not self.commandQueue.empty():
            
            print "Power is {}, active is {}, desired is {}".format(powerState, activeState, desiredState)
            command = self.commandQueue.get(False)
            if command == 'toggle' and (activeState == 'raspi' or powerState == 'off'):
                if powerState == 'on':
                    self.__setDesiredPowerState__('off')
                else:
                    self.__setDesiredPowerState__('on')
                print "Asked for power to toggle"
            elif command == 'turnOn':
                self.__setDesiredPowerState__('on')
                print "Asked for power on"
            elif command == 'turnOff' and activeState == 'raspi':
                self.__setDesiredPowerState__('off')
                print "Asked for power off"
            else:
                # Not in the right state or the command isn't valid
                print 'Rejecting command because TV is not on computer input'
              
            # print "Command received in thread - command was {}".format(command)



      #  self.stateSafeSemaphore.acquire()
      #  safeState = self.safeToDetermineState 
      #  self.stateSafeSemaphore.release()

      #  if safeState:
        # print "In safe state"
        if powerState == 'on':
            if desiredState == 'off':
                self.process.sendline('standby 0')
                print "Turning off"
            else:
                pass # Do nothing, we're where we want to be.
               # print "Doing nothing - power is already on"
        else:
            if desiredState == 'off':
                pass # do nothing 
              #  print "Doing nothing - power is already off"
            else:
                print "Turning on"
                self.process.sendline('as')
       # else:
        #    print "Not safe state"
            
    def __setDesiredPowerState__(self, desired_state):
        self.powerDesiredSemaphore.acquire()
        self.desiredPowerState = desired_state
        self.powerDesiredSemaphore.release()  
        
    def __getDesiredPowerState__(self):
        self.powerDesiredSemaphore.acquire()
        desired_state = self.desiredPowerState 
        self.powerDesiredSemaphore.release()   
        
        return desired_state
        
    def __setPowerState__(self, state_val):
        self.powerSemaphore.acquire()
        self.powerState = state_val
        self.powerSemaphore.release()
        
    def __getPowerState__(self):
        self.powerSemaphore.acquire()
        powerState = self.powerState
        self.powerSemaphore.release()
        
        return powerState
        
    def __setActiveState__(self, state_val):
        self.stateSemaphore.acquire()
        self.activeState = state_val
        self.stateSemaphore.release()
                        
    def __getActiveState__(self):
        self.stateSemaphore.acquire()
        activeState = self.activeState
        self.stateSemaphore.release()
        
        return activeState
    

    def __tv_state_monitor__(self):

      lastRead = time.time()
      standby_requested = False
      active_requested = False
      while 1:
        if not self.cecQueue.empty():
        
            lastRead = time.time()
          #  self.stateSafeSemaphore.acquire()
           # self.safeToDetermineState = False
           # self.stateSafeSemaphore.release()
            stdout = self.cecQueue.get()
            # print stdout
            
            if re.match(".*as.*", stdout):
                #print "as requested"
                active_requested = True
            if re.match(".*standby 0.*", stdout):
                print "standby requested"
                standby_requested = True
            
            if re.match(".*?power status changed.*to 'on'.*?", stdout) or re.match(".*in transition from standby to on.*", stdout):
                # print "Power turned on"
                # Clear the queue
                self.__setPowerState__('on')
                # Put the latest state in the queue
                print "Putting power on"
                if not standby_requested:
                    self.__setDesiredPowerState__('on')
                active_requested = False
              
            elif re.match(".*?power status changed.*to 'standby'.*?", stdout):
                # print "Power turned off"
                # Clear the queue
                
                # Put the latest state in the queue
                print "Putting power off"
                if not standby_requested:
                    self.__setDesiredPowerState__('off')
                standby_requested = False
                
                self.__setPowerState__('off')
              
            elif re.match(".*?making tv.*the active source.*?", stdout):
                print "raspi is not the active source"
                # Put the latest state in the queue
                print "Putting not_raspi"
                self.__setActiveState__('not_raspi')
            elif re.match(".*?making recorder.* the active source.*?", stdout):
                print "raspi is the active source"
                # Put the latest state in the queue
                print "Putting raspi"
                self.__setActiveState__('raspi')
        else:
            if (time.time() - lastRead) > 3.5:
                pass            
              #  self.stateSafeSemaphore.acquire()
              #  self.safeToDetermineState = True
              #  self.stateSafeSemaphore.release()
              
  #  def tvIsOn(self):
   #     self.stateSafeSemaphore.acquire()
    #    safeState = self.safeToDetermineState 
    #    self.stateSafeSemaphore.release()
#
#      if not self.powerQueue.empty() :
#        self.powerState = self.powerQueue.get()
      # If nothing has changed, the queue will be empty and the state 
      # won't have changed
        
#      return self.powerState 
            
#    def computerIsActive(self):

#      self.stateSafeSemaphore.acquire()
#      safeState = self.safeToDetermineState 
#      self.stateSafeSemaphore.release()

 #     if not self.activeQueue.empty() :
 #         self.activeState = self.activeQueue.get()
      # If nothing has changed, the queue will be empty and the state 
      # won't have changed
        
  #    return self.activeState
            
    def toggleScreen(self):
        self.commandQueue.put('toggle', False)
        pass
      
    def turnOnScreen(self):
        self.commandQueue.put('turnOn', False)
      
    def turnOffScreen(self):
        print "Turn off was asked for"
        self.commandQueue.put('turnOff', False)
      
    def askForTvOn(self, nextNSeconds):
        sleep(5)
        powerState = self.__getPowerState__()
        activeState = self.__getActiveState__()
        
        print "Power is {}, active is {} in askForTV".format(powerState, activeState)
        
        if powerState == 'on' and activeState == 'raspi':
            # Good, we're in the state we need to be in. 
            # Turn it off in nextNSeconds seconds
            "TV is already on"
            self.turnOnScreen()
            threading.Timer(nextNSeconds, self.turnOffScreen).start()
        elif activeState != 'raspi' and powerState == 'on':
            # Not on the raspberry pi and TV is on
            # Wait a minute and try again
            waitTime = 3
            print "Can't turn TV on, not active source"
            threading.Timer(waitTime, self.askForTvOn, [nextNSeconds - waitTime]).start()
        else: #  powerState == 'off'
            print "Turning on TV as asked for"
            self.turnOnScreen()
            threading.Timer(nextNSeconds, self.turnOffScreen).start()
      
if __name__ == "__main__":  
    ccl = tvStateManager()

    while 1:
        sys.stdout.flush()
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        filename = raw_input()
        if filename.lower() == 'on':
            ccl.turnOnScreen()
        elif filename.lower() == 'toggle':
            ccl.toggleScreen()
        elif filename.lower() == 'off':
            ccl.turnOffScreen()
        elif filename.lower() == 'askon':
            ccl.askForTvOn(160)


