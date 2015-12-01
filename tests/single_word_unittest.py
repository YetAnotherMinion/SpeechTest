import unittest
import os, sys, inspect
import yaml
import itertools
import subprocess
import time
import datetime

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

#import path hacks required to read the code sitting in the src directory
G_TEST_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
(G_PROJECT_ROOT_DIR,tail) = os.path.split(G_TEST_DIR)
if G_PROJECT_ROOT_DIR not in sys.path:
     sys.path.insert(0, G_PROJECT_ROOT_DIR)

from src.demo import decode_from_file
from src.util import suppress_stdout_stderr

# Define a context manager to suppress stdout and stderr.

class TestSingleWord(unittest.TestCase):
    def setUp(self):
        MODELDIR = "pocketsphinx/model"
        DATADIR = "pocketsphinx/test/data"

        # Create a decoder with certain model
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
        config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
         # Decode streaming data.
        try:
            self.decoder = Decoder(config)
        except RuntimeError:
            time.sleep(1) # try waiting and trying again
            self.decoder = Decoder(config)

    def test_single_words(self):
        in_file = os.path.join(G_TEST_DIR, 'command_words.yml')
        with open(in_file, 'r') as f:
            testcases = yaml.safe_load(f)

        def flatten(container):
            if isinstance(container, basestring):
                yield (container,)
                raise StopIteration()
            try:
                for key,value in container.items():
                    for item in flatten(value):
                        yield (key,) + item
            except AttributeError:
                for value in container:
                    for item in flatten(value):
                        yield item

        word_score = {}
        count = 0

        for tc in flatten(testcases):
            sample_word = tc[-1]
            count += 1
            if not sample_word in word_score:
                word_score[sample_word] = {"correct":0, "total":1}
            else:
                word_score[sample_word]["total"] += 1
            fn = os.path.join(G_PROJECT_ROOT_DIR, *tc[0:-1])
            print fn
            with suppress_stdout_stderr():
                x = decode_from_file(fn, self.decoder)

            if x.hypothesis.hypstr == sample_word:
                word_score[sample_word]["correct"] += 1

        tmp_array = [x for x in word_score.items()]
        tmp_array.sort(reverse = True, key = lambda y: (float(y[1]["correct"])/ float(y[1]["total"])*100) )

        #find out what commit we are running under
        label = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        label = lable.strip('\n')
        time_label = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d|%H:%M:%S')
        out_fn = "".join(label) + "_" + time_label + ".yml"
        with open(out_fn, "w") as f:
            f.write(yaml.dump(word_score))

        row_format = "|{:<10}|{:>7}" + " | " + "{:>6.4} |" 
        print "|_.Command |_.Correct/Total |_.%Correct |"
        for key,value in tmp_array:
            ratio = "{}/{}".format(value["correct"], value["total"])
            print row_format.format(key, ratio, (float(value["correct"])/ float(value["total"])*100))

if __name__ == '__main__':
    unittest.main()
