import yaml
import os, sys

print os.walk("res/")

for (dirpath, dirnames, filenames) in os.walk("res/"):
	print dirpath
	print dirnames
	print filenames
	print "="*50
