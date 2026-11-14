"created by AditiJindal 09-20-2026"

import os
from pathlib import Path 
from psychopy import prefs
from psychopy.hardware import keyboard

#ALL PATHS HERE
ROOT_DIR_ADITI= Path(r"C:\Users\aditi\Downloads\CONNECTLAB\auditory_task_button_version") #change later 
ROOT_DIR_STIM_PC = Path(r"C:\Users\Connect\Documents\spatial_attention\EEG-fMRI-auditory-task--main") 
STIM_PATH = ROOT_DIR_ADITI/"stim_files" #change on STIMPC later 
DATA_PATH = ROOT_DIR_ADITI/"data"

SCANNER_NOISE_PATH = STIM_PATH/"noise"/"testing_noise.wav" #sample noise approx 5 mins long 
target1_path = STIM_PATH/"target"/"target1.wav" 
target2_path = STIM_PATH/"target"/"target2.wav"

stim_duration = 2.980045351473923 #hardcoded

params = {}  #anything related to the actual trial 

#AttR; target only from right), attend left (AttL; target only from left), and attend non-directionally (AttND; target from either side).
params["conditions"] = ["AttR", "AttL", "AttND"] #saved as list 
params["trials_per_block"] = 40
params["inter-block_wait_time"] = 0.0 
params["attnd_aud_split"] = 0.5 #for last trial, split between sides 
params["target_types"] = ["target1", "target2"]  
params["target_ratio"] = 0.5 #target 1 vs target 2 ratio 
params["min_ITI_long"] = 20
params["max_ITI_long"] = 35
params["min_ITI_short"] = 5
params["max_ITI_short"] = 10
params["short_to_long_ITI_ratio"] = 0.15 #6 trials 


#constants 
params["incentive_value"] = 10 
params["default_sample_rate"] = 44100 #both audios match this  might move to hware later idk
params["post_trial_wait_time"] = 0.3  #time to wait after trial finishes playing for response before moving on
params["feedback_duration"] = 0.3 # in seconds 
# _______________________________________________________ Set Screen Parameters 
scr = {

    "white": [1, 1, 1],                                 # Fixation cross / text
    "grey": [0, 0, 0],                                  # Fixation cross / text
    "darkgrey": [-0.5, -.5, -.5],                       # Brighter background
    "black": [-1, -1, -1],                              # Background
    "red": [0.83, 0, 0],                                # FA;  luminance 50%
    "green": [0, 0.42, 0],                              # Hit; luminance 50%
    "yellow": [0.49, 0.49, 0],                          # Miss
    "dist": 50,                                         # cm
    "width": 30,                                        # cm
    "skipChecks": False,                                # Equivalent for timing checks
}

#fill in with hware preferences -> later after trial starts working 
hware  = {}
# ---------------------------------------------------------------------------
# Response keys
# ---------------------------------------------------------------------------

hware["keys"] = {} 
#hware["keys"]["detection_key_left"] = "left" 
#hware["keys"]["detection_key_right"] = "right"
hware["keys"]["detection_key_left"] = [65531]
hware["keys"]["detection_key_right"] = [65527] 
hware["keys"]["detection_key_release"] = [65535] 
hware["keys"]["quit_key"]= "escape"
hware["keys"]["wait_key"]= "space"

hware["aditimon_size"] = (2880, 1800) 







