import unittest
import os, sys, inspect

#import path hacks required to read the code sitting in the src directory
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
(root_folder,tail) = os.path.split(cmd_folder)
if root_folder not in sys.path:
     sys.path.insert(0, root_folder)

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
	def test_goforward(self):
		with suppress_stdout_stderr():
			fn = os.path.join(root_folder, 'res', 'goforward.raw')
			x = decode_from_file(fn)
		print ('Best hypothesis: ', x.hypothesis.hypstr, " model score: ", x.hypothesis.best_score, " confidence: ", x.hypothesis.prob)
		print ('Best hypothesis segments: ', x.hypothesis_segments)

		# Access N best decodings.
		print ('Best 10 hypothesis: ')
		for i, best in x.nbest:
		    print (best.hypstr, best.score)

if __name__ == '__main__':
	unittest.main()
