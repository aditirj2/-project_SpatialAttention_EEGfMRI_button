import random
import numpy as np
from psychopy import data, core, event, sound, visual

import config
import stimuli
import instructions 
import dichotic_task 
import pylsl

# ---------------------------------------------------------------- tunables
N_TRIALS_PER_STAIR = 10         # 2 staircases -> 20 trials minimum, this number does not matter as much
START_SNRS = [1.0, 0.03]         # linear: easy (0 dB) and hard (~ -30 dB)
STEP_SIZES_DB = [6, 3, 2, 1]     # big steps first, shrink after each reversal last 9 reversals are step size 1 
MIN_SNR, MAX_SNR = 0.003, 3.0    # clamp so the staircase can't run away

N_REVERSALS_PER_STAIR = 12       # in order for staircase to complete must have 12 reversals 
N_REVERSALS_FOR_ESTIMATE = 8     # average the last 8, dropping the first 4 coarse-step ones as the step sizes are too big 
MAX_TOTAL_TRIALS = 100  #hard break 

LOW_ITI = 5                   
HIGH_ITI = 15

def _build_target(raw_target, rms_noise, snr, side): #returns playable sound object in specific ear adjusted for SNR 
    """Scale one target to `snr` relative to the noise and place it on one ear."""
    rms_signal = stimuli._compute_RMS(raw_target)
    sf = stimuli._compute_sf(snr, rms_noise, rms_signal)
    scaled = stimuli._scale_audio(raw_target, sf)
    return stimuli._build_stero_arr(scaled, side) #returns np arr must load into sound.Sound 


def _estimate_threshold(stairs):
    """Geometric mean (= mean in dB) of the last few reversals, pooled over both staircases."""
    log_vals = []
    for stair in stairs.staircases:
        revs = list(stair.reversalIntensities)
        if len(revs) >= 2:
            revs = revs[-N_REVERSALS_FOR_ESTIMATE:]
        else:                                   # too few reversals -> fall back to late trials
            revs = list(stair.intensities)[-10:]
        log_vals.extend(np.log10(revs))
    return float(10 ** np.mean(log_vals))


def staircase(win, params, hware, run_onset):
    # ---- load raw audio ONCE (RMS and resampling are slow; don't redo per trial)
    raw = stimuli.load_all_audio(config.SCANNER_NOISE_PATH, config.target1_path,
                                 config.target2_path, params["default_sample_rate"])
    noise_arr = raw["noise"]["data"]
    rms_noise = stimuli._compute_RMS(noise_arr)
    targets = {"target1": raw["target1"], "target2": raw["target2"]}

    # ---- background noise loops for the whole procedure (same settings as load_sound)
    noise = sound.Sound(noise_arr, loops=-1, sampleRate=params["default_sample_rate"],
                        volume=0.1, stereo=True)

    # ---- the double staircase
    conditions = [
        {"label": f"stair{i+1}", "startVal": start, "nUp": 1, "nDown": 2,
         "stepType": "db", "stepSizes": STEP_SIZES_DB,
         "minVal": MIN_SNR, "maxVal": MAX_SNR, "nTrials": N_TRIALS_PER_STAIR, "nReversals" : N_REVERSALS_PER_STAIR}
        for i, start in enumerate(START_SNRS) #2 staircases 
    ]
    
    stairs = data.MultiStairHandler(stairType="simple", method="random",
                                    conditions=conditions, nTrials=N_TRIALS_PER_STAIR)

    #loading keys -> subject to change 
    left_key = hware["keys"]["detection_key_left"]
    right_key = hware["keys"]["detection_key_right"]
    visual_stims = [visual.TextStim(win, text="+", height=0.1, color=config.scr["white"]), 
                                stimuli.visual_stim(win, params, hware, "left"), stimuli.visual_stim(win, params, hware, "right")] 
#   pressed_visual_stims = [visual.TextStim(win, text="+", height=0.1, color=config.scr["black"]), 
#                                stimuli.visual_stim(win, params, hware, "left"), stimuli.visual_stim(win, params, hware, "right")]
    feedback_dur = params["feedback_duration"] 
    
    #play background noise on loop 
    noise.play(loops=5) #about 5 minutes would need to loop it 5 times 
    #draw calibration start screen
    instructions.starting_calibration_instructions(win, params, hware) 
    #draw AttND screen
    stimuli.draw_all(visual_stims); win.flip()
    
    #staircase loop func hands back the next SNR to test depending on response 
    trial_ct = 1
    for snr, cond in stairs:  
        
        if trial_ct > MAX_TOTAL_TRIALS :
            break 
        
        side = random.choice(["left", "right"])
        name = random.choice(["target1", "target2"])
        iti = random.uniform(LOW_ITI, HIGH_ITI) 
        
        stim = sound.Sound(_build_target(targets[name]["data"], rms_noise, snr, side),
                           sampleRate=params["default_sample_rate"], volume=0.1, stereo=True) 
        dur = targets[name]["duration"] #same for both targets 

        # inter-trial wait -> random 
        core.wait(iti) 
        clock = core.Clock() 
        trial_onset = pylsl.local_clock()
        stim.play()
        keys, raw_data, false_alarms = dichotic_task.pull_stim_response(hware, run_onset, trial_onset, dur + params["post_trial_wait_time"])
        print(keys)
        
        #if pressed 
        if keys != None :
            stimuli.feedback_flip(win, params, hware, (keys[0] == side), "both", time_left_in_trial = None) 
    
        #if not pressed 
        elif keys == None : 
            stimuli.feedback_flip(win, params, hware, 0, "both", time_left_in_trial = None) 
        
        
        
#        #if pressed -> change screen to black arrow instead 
#        if keys != None :
#            #change screen to black for millisecond 
#            stimuli.draw_all(pressed_visual_stims); 
#            win.flip()
#            core.wait(feedback_dur)
#            stimuli.draw_all(visual_stims); win.flip()

        correct = int(keys is not None and keys[0] == side)   # no response counts as wrong -> rewrite based off what makes sense to me 
        stairs.addResponse(correct)

        remaining = dur - clock.getTime()          # let the sound finish before next trial
        if remaining > 0:
            core.wait(remaining)
        stim.stop()
        #add trial count 
        trial_ct+=1
        
    #print data for review 
    for i, stair in enumerate(stairs.staircases):
        print(f"printing staircase data results: {i}") 
        n_trials = len(stair.data)
        print(f"number of trials: {n_trials}") 
        #print(stair.intensities)  #is the SNR played on every trial, in order. It’s the staircase’s trajectory, starting at 1.0 (or 0.03) and moving up and down. Its length is the number of trials handed out, which can be one more than the number answered if the cap fired.
        print(f"SNR @ each reversal: {stair.reversalIntensities}") #is the SNR at each reversal trial. Its length is the number of reversals, and the last 8 values are what get averaged. This is the line to compare between stair1 and stair2.
        #print(stair.data) # is the 1 (correct) or 0 (wrong) result for each answered trial, in the same order as intensities. Its length is the true number of trials answered, and its average is the proportion correct.
        
    noise.stop()
    #draw calibration complete screen -> print SNR 
    instructions.end_calibration_instructions(win, params, hware)
    win.flip()
    snr_estimate = _estimate_threshold(stairs) 
    
    #print(f"SNR = {snr_estimate:.4f} ({20*np.log10(snr_estimate):.1f} dB)")
    return snr_estimate
