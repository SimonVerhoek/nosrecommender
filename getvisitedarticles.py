#!/usr/bin/env python

import os.path

fileName = "urlsonly.json"

def checkIfFileExists(fileName):
	if os.path.isfile(fileName):
		return "file exists"
	else:
		return "file does not exist"

print checkIfFileExists(fileName)