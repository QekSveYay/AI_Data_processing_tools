#################################################################
#
# Goal: to automatically create veri_test.tx in VoxCeleb dataset
#
#################################################################
import os
import numpy as np

# trial number per utterance; one positive and one negative per trial
trial_per_utter = 4
trial_pair_filename = 'veri_test.txt'
# source directory
src = '\dataset\VoxCeleb1'

# get the absolute path of the source directory
src = os.path.abspath(src)

# variable having the index till which src string has directory and a path separator
src_prefix = len(src) + len(os.path.sep)

utter_pair = {}
# doing os walk in source directory
for root, dirs, files in os.walk(src):
    for filename in files:
        if 'wav' in filename:
            id_filepath = os.path.join(root[src_prefix:], filename)
            utter_pair[id_filepath] = root[src_prefix:]

f = open(trial_pair_filename, 'w')
utter_pair_len = len(utter_pair)
id_filepath_list = list(utter_pair.keys())
for id_filepath in utter_pair:
    for i in range(trial_per_utter):
        not_found = True
        while not_found:
            filenum = np.random.randint(1, utter_pair_len)
            if utter_pair[(id_filepath_list[filenum])] == utter_pair[id_filepath]:
                # find utterance from the same person
                pair_list = '1 ' + id_filepath + ' ' + id_filepath_list[filenum] + '\n'
                not_found = False
        f.write(pair_list)
        not_found = True
        while not_found:
            filenum = np.random.randint(1, utter_pair_len)
            if utter_pair[(id_filepath_list[filenum])] != utter_pair[id_filepath]:
                # find utterance from the same person
                pair_list = '0 ' + id_filepath + ' ' + id_filepath_list[filenum] + '\n'
                not_found = False
        f.write(pair_list)
f.close()