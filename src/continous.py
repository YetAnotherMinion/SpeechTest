import unittest
import os, sys, inspect
import yaml
import itertools
import subprocess
import time
import datetime

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
from demo import loop_decode

#import path hacks required to read the code sitting in the src directory
G_TEST_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
(G_PROJECT_ROOT_DIR,tail) = os.path.split(G_TEST_DIR)
if G_PROJECT_ROOT_DIR not in sys.path:
     sys.path.insert(0, G_PROJECT_ROOT_DIR)

from src.demo import loop_decode
from util import suppress_stdout_stderr

def continous():
    MODELDIR = "pocketsphinx/model"
    DATADIR = "pocketsphinx/test/data"

    # Create a decoder with certain model
    config = Decoder.default_config()
    config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
    config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
     # Decode streaming data.
    try:
    	with suppress_stdout_stderr():
        	decoder = Decoder(config)
    except RuntimeError:
        time.sleep(1) # try waiting and trying again
        decoder = Decoder(config)

    looper = loop_decode(decoder=decoder)
    x = looper.next()
    print x
    x = looper.next()
    print x

if __name__ == '__main__':
	continous()
