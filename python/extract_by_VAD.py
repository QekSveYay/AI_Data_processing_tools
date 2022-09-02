import os
import struct
import webrtcvad
import numpy as np
from scipy.io import wavfile

src = "/voice_data/a"    # source wav dataset
dst = "/voice_data/vad/a"    # target VAD folder
waveread_method = 'scipy'    # scipy, wave
webrtcvad_mode = 2    # 0, 1, 2; check webrtcvad document for more details

######################## wavRead WAVE version #########################
import wave

def wavRead(fileN):
  waveFile = wave.open(fileN, 'r')
  NbChanels = waveFile.getnchannels()
  data = []
  for x in range(NbChanels):
      data.append([])
  for i in range(0,waveFile.getnframes()):
      waveData = waveFile.readframes(1)
      data[i%(NbChanels)].append(int(struct.unpack("<h", waveData)[0]))

  RetAR = []
  BitDebth = waveFile.getsampwidth()*8
  for x in range(NbChanels):
       RetAR.append(np.array(data[x]))
       # Convert to floating point
       #RetAR[-1] = RetAR[-1]/float(pow(2,(BitDebth-1)))
  fs = waveFile.getframerate()
  return fs, RetAR
#######################################################################

def reduce_silence_by_VAD(input_file, out_file):
    if waveread_method == 'wave':
        # use python wave module to read wav files
        sample_rate, wav_samples = wavRead(input_file)
        samples = wav_samples[0]
    elif waveread_method == 'scipy':
        # use scipy module to read wav files
        sample_rate, samples = wavfile.read(input_file)

    vad = webrtcvad.Vad()
    vad.set_mode(webrtcvad_mode)

    raw_samples = struct.pack("%dh" % len(samples), *samples)

    window_duration = 0.03    # duration in seconds 0.03
    samples_per_window = int(window_duration * sample_rate + 0.3)
    bytes_per_sample = 2

    segments = []
    flag_vad = False    # keep information of voice active or not
    try:
        for start in np.arange(0, len(samples), samples_per_window):
            stop = min(start + samples_per_window, len(samples))
            is_speech = vad.is_speech(raw_samples[start * bytes_per_sample: stop * bytes_per_sample],
                                      sample_rate = sample_rate)
            segments.append(dict(
                    start = start,
                    stop = stop,
                    is_speech = is_speech))
            if is_speech == True:
                flag_vad = True    # update VAD information
    except:
        print(input_file+' sent error when reduce silence')
    if flag_vad == True:
        speech_samples = np.concatenate([ samples[segment['start']:segment['stop']] for segment in segments if segment['is_speech']])
        wavfile.write(out_file, sample_rate, speech_samples)

# getting the absolute path of the source
# directory
src = os.path.abspath(src)
dst = os.path.abspath(dst)

# making a variable having the index till which
# src string has directory and a path separator
src_prefix = len(src) + len(os.path.sep)

# making the destination directory
os.makedirs(dst)

# doing os walk in source directory
for root, dirs, files in os.walk(src):
    for dirname in dirs:

        # here dst has destination directory,
        # root[src_prefix:] gives us relative
        # path from source directory
        # and dirname has folder names
        dst_dirpath = os.path.join(dst, root[src_prefix:], dirname)

        # making the path which we made by
        # joining all of the above three
        os.mkdir(dst_dirpath)

    for filename in files:
        if 'wav' in filename:
            # perform VAD only for wav files
            src_filepath = os.path.join(src, root[src_prefix:], filename)
            dst_filepath = os.path.join(dst, root[src_prefix:], filename)
            reduce_silence_by_VAD(scr_filepath, dst_filepath)
