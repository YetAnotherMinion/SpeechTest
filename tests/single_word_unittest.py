import unittest
import os, sys, inspect
import yaml
import itertools

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

#import path hacks required to read the code sitting in the src directory
G_TEST_DIR = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
(G_PROJECT_ROOT_DIR,tail) = os.path.split(G_TEST_DIR)
if G_PROJECT_ROOT_DIR not in sys.path:
     sys.path.insert(0, G_PROJECT_ROOT_DIR)

from src.demo import decode_from_file

# Define a context manager to suppress stdout and stderr.
class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in 
    Python, i.e. will suppress all print, even if the print originates in a 
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).      

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

class TestSingleWord(unittest.TestCase):
    def setUp(self):
        pass
    # def test_goforward(self):
    #     with suppress_stdout_stderr():
    #         fn = os.path.join(G_PROJECT_ROOT_DIR, 'res', 'goforward.raw')
    #         x = decode_from_file(fn)
    #     print ('Best hypothesis: ', x.hypothesis.hypstr, " model score: ", x.hypothesis.best_score, " confidence: ", x.hypothesis.prob)
    #     print ('Best hypothesis segments: ', x.hypothesis_segments)

    #     # Access N best decodings.
    #     print ('Best 10 hypothesis: ')
    #     for i, best in x.nbest:
    #         print (best.hypstr, best.score)

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

        MODELDIR = "pocketsphinx/model"
        DATADIR = "pocketsphinx/test/data"

        # Create a decoder with certain model
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
        config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))

        # Decode streaming data.
        try:
            decoder = Decoder(config)
        except RuntimeError:
            time.sleep(1) # try waiting and trying again
            decoder = Decoder(config)

        for tc in flatten(testcases):
            sample_word = tc[-1]
            count += 1
            if not sample_word in word_score:
                word_score[sample_word] = [0, 1]
            else:
                word_score[sample_word][1] += 1
            fn = os.path.join(G_PROJECT_ROOT_DIR, *tc[0:-1])
            print fn
            with suppress_stdout_stderr():
                x = decode_from_file(fn, decoder)

            if x.hypothesis.hypstr == sample_word:
                word_score[sample_word][0] += 1

        row_format = "{:<10}{:>7}" + " "*4 + "{:>.4}"
        for key,value in word_score.items():
            ratio = "{}/{}".format(value[0], value[1])
            print row_format.format(key, ratio, (float(value[0])/ float(value[1])*100))


if __name__ == '__main__':
    unittest.main()
