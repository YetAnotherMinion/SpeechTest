from os import environ, path
import time
import pyaudio
import wave
from util import suppress_stdout_stderr
import datetime


from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

class CandiateUtterance(object):
    def __init__(self):
        self.hypothesis = None
        self.hypothesis_segments = []
        self.nbest = []
        self.elasped_time = None

def decode_from_file(filename, decoder = None):
    if decoder == None:
        MODELDIR = "pocketsphinx/model"
        DATADIR = "pocketsphinx/test/data"

        # Create a decoder with certain model
        config = Decoder.default_config()
        config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
        config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))

        # Decode streaming data.
        try:
            decoder = Decoder(config)
        except RuntimeError:
            time.sleep(1) # try waiting and trying again
            decoder = Decoder(config)

    # print ("Pronunciation for word 'hello' is ", decoder.lookup_word("hello"))
    # print ("Pronunciation for word 'abcdf' is ", decoder.lookup_word("abcdf"))

    decoder.start_utt()
    with open(filename, 'rb') as stream:
        while True:
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
            else:
                break
        decoder.end_utt()

    cu = CandiateUtterance()
    cu.hypothesis = decoder.hyp()
    cu.hypothesis_segments = [seg.word for seg in decoder.seg()]
    cu.nbest = zip(range(10), decoder.nbest())
    return cu

def loop_decode(seconds = 3, decoder = None):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = seconds
    cu = None
    try:
        while True:
            yield cu
            with suppress_stdout_stderr():
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            print("* recording")
            frames = []
            n_frames = int(RATE / CHUNK * RECORD_SECONDS)
            for i in range(0, n_frames):
                data = stream.read(CHUNK)
                frames.append(data)
                if not i%10:
                    print i
            print("* done recording")
            n1 = datetime.datetime.now()
            stream.stop_stream()
            stream.close()
            p.terminate()
            with suppress_stdout_stderr():
                n1 = datetime.datetime.now()
                decoder.start_utt()
                print "Frame length:", len(frames)
                for buf in frames:
                    if buf:
                        decoder.process_raw(buf, False, False)
                    else:
                        break
                decoder.end_utt()
                del frames

                cu = CandiateUtterance()
                cu.hypothesis = decoder.hyp()
                cu.hypothesis_segments = [seg.word for seg in decoder.seg()]
                cu.nbest = zip(range(10), decoder.nbest())
                n2 = datetime.datetime.now()
                cu.elasped_time = (n2-n1).microseconds
            
    except GeneratorExit:
        #finished
        pass

# stream = open(path.join(DATADIR, 'goforward.mfc'), 'rb')
# stream.read(4)
# buf = stream.read(13780)
# decoder.start_utt()
# decoder.process_cep(buf, False, True)
# decoder.end_utt()
# hypothesis = decoder.hyp()
# print ('Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", hypothesis.prob)
