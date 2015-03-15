#!/usr/bin/env python

import os.path
import time

fileName = "urlsonly.json"

interval = 1

# define the function that is to be executed
# it will be executed in a thread by the scheduler
def checkIfFileExists():
	time.sleep(interval)
	
	if os.path.isfile(fileName):
		print "file exists"
	else:
		print "file does not exist"
		checkIfFileExists()


checkIfFileExists()
