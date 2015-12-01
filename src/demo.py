# ====================================================================
# Copyright (c) 2013 Carnegie Mellon University.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer. 
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# This work was supported in part by funding from the Defense Advanced 
# Research Projects Agency and the National Science Foundation of the 
# United States of America, and the CMU Sphinx Speech Consortium.
#
# THIS SOFTWARE IS PROVIDED BY CARNEGIE MELLON UNIVERSITY ``AS IS'' AND 
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CARNEGIE MELLON UNIVERSITY
# NOR ITS EMPLOYEES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ====================================================================


from os import environ, path
import time


from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

class CandiateUtterance(object):
    def __init__(self):
        self.hypothesis = None
        self.hypothesis_segments = []
        self.nbest = []

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
    try:
        while True:
            fn = "o"+str(x)+".wav"
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            print("* recording")
            frames = []
            n_frames = int(RATE / CHUNK * RECORD_SECONDS)
            for i in range(0, n_frames):
                print i
                data = stream.read(CHUNK)
                frames.append(data)
            print("* done recording")
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            decoder.start_utt()
            for buf in frames:
                if buf:
                    decoder.process_raw(buf, False, False)
                else:
                    break
            decoder.end_utt()

            cu = CandiateUtterance()
            cu.hypothesis = decoder.hyp()
            cu.hypothesis_segments = [seg.word for seg in decoder.seg()]
            cu.nbest = zip(range(10), decoder.nbest())
            yield cu

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
