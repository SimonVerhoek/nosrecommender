#!/usr/bin/env python

import os.path
import time

fileName = "urlsonly.json"

interval = 1

def checkIfFileExists():
	time.sleep(interval)
	
	if os.path.isfile(fileName):
		print "file exists"
	else:
		print "file does not exist"
		checkIfFileExists()


checkIfFileExists()
