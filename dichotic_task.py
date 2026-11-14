import numpy 
import config
import predetermined
import instructions 
import stimuli
from psychopy import visual, core, event 
from psychopy import sound 
import pylsl
import trigger 

#calculated but not added to results 
def _correct_Keys(key_pressed, cue_side_aud) :
    if key_pressed == None :
        return 0 
    if key_pressed == cue_side_aud : 
        return 10
    else :
        return -10 

def get_time(stim_start) : 
    return pylsl.local_clock() - stim_start 
    
        
def _mp_to_side_convert(marker_press_code, hware): 
    if marker_press_code == hware["keys"]["detection_key_left"] :
        return "left" 
    elif marker_press_code == hware["keys"]["detection_key_right"] :
        return "right" 
    elif marker_press_code == hware["keys"]["detection_key_release"] :
        return None
    return str(marker_press_code[0]) #convert to raw string so can make it onto list and be comparable 
    
def _mp_list_convert(marker_presses, hware) :
    markers_converted = [] 
    for marker in marker_presses :
        markers_converted.append(_mp_to_side_convert(marker, hware)) 
    return markers_converted 

def pull_responses(hware, run_onset) :  #ignore the button release press returns key pairs similar to waitkeys
    
    samples = []
    timestamp_lsl = []
    m_press, times = trigger.pullMarkers(hware)  # this function automatically flushes 
    
    m_convert = _mp_list_convert(m_press, hware) #converts marker presses to left and right 

    for i, marker in enumerate(m_convert) : 
        if marker != None: 
            samples.append(marker)
            timestamp_lsl.append(times[i] - run_onset) # does not return raw time time in reference to start time of run 

    raw = list(zip(m_press, times))
    iti_mp = list(zip(samples, timestamp_lsl)) #saves them as tuples 

    return iti_mp, raw #returns in the form of keys... need to figure out what how results.py is added on to this 
    
#TO FIX -----------
def pull_stim_response(hware, run_onset, trial_onset, max_wait_time) : #run onset for time, trial onset for rt max wait time is how long stim will run 
    
    raw_responses = []
    false_alarms = []
    rt_win_end = trial_onset + max_wait_time 
    while pylsl.local_clock() < rt_win_end : #while current time stays under lsl + suspected duration 
        core.wait(.01) #wait 10 ms before checking again 
        responses, raw = pull_responses(hware, run_onset) 
        raw_responses.extend(raw) 
    
        for i, response in enumerate(responses): 
            response_lsl = response[1] + run_onset 
            if response_lsl > trial_onset and response_lsl < rt_win_end : #checks if response is larger than when trial starts 
                key_pressed = response[0]
                onset = response[1]
                rt = (onset + run_onset) - trial_onset  
                response = key_pressed, onset, rt 
                false_alarms.extend(responses[i+1:]) #design flaw... some trials might be counted as current trial and some as next... figure out later 
                return response, raw_responses, false_alarms 
            else:
                key_pressed = response[0]
                onset = response[1]
                false_alm = key_pressed, onset
                false_alarms.append(false_alm)
        continue 

    #nothing caught, return none 
    return None , raw_responses, false_alarms

def append_raw_mp(raw_keys_list, results_list, run_onset) :

    for i in raw_keys_list : 
        results_dict = {}
        results_dict['raw_marker'] = i[0]
        results_dict['raw_timestamp_lsl'] = i[1]
        results_dict['corrected_time'] = i[1] - run_onset 
        results_list.append(results_dict)    

def append_iti_mp(iti_keys_list, results_list, trial_info) : #make a copy so prev info doesn't get changed
    
    for i in iti_keys_list : 
        new_row = trial_info.copy()
        new_row["data_type"] = "false_alrm"
        new_row["key_pressed"] = i[0]
        new_row["button_p_onset"] =  i[1]
        new_row["correct"] = 0 #boolean value 
        results_list.append(new_row) 


def dichotic_task_block(win, block, audio, params, hware, SNR, run_onset, running_tally) : #run onset = t0_lsl
    
    keys = ["participant_id", "trial_num", "condition", "stim_dur", "ITI",
            "cue_side_vis", "cue_side_aud", "target_type", "SNR"]  # final predetermined.py keys

    possible_keys_rt = [hware["keys"]["detection_key_left"], hware["keys"]["detection_key_right"]]
    tally = running_tally 
    
    results_per_block = []
    raw_rpb = []
    
    
    #flush all button markers before trial starts 
    hware['button'].flush()
    
    for trial in block: #each element in block is a dictionary
    
        #extract elements per trial 
        condition = trial[keys[2]]
        stim_dur = trial[keys[3]]
        iti = trial[keys[4]] #this trial ITI 
        cue_side_vis = trial[keys[5]]
        cue_side_aud = trial[keys[6]]
        target_type = trial[keys[7]] 
        
        #in case trial RT needs longer time post stim end 
        trial_wait_time = stim_dur + config.params["post_trial_wait_time"] #approx 3.3 seconds of wait time 
        
        #load visual stim 
        if cue_side_vis == "both" : #@aditirj 10-7-2026 adding visual stim to both sides 
            vis = [stimuli.visual_stim(win, params, hware, "left"), stimuli.visual_stim(win, params, hware, "right"), visual.TextStim(win, text="+", height=0.1, color=config.scr["white"])]
            stimuli.draw_all(vis) 
        else :
            vis = [stimuli.visual_stim(win, params, hware, cue_side_vis), visual.TextStim(win, text="+", height=0.1, color=config.scr["white"])]
            stimuli.draw_all(vis) 
        
        #load audio stim   ["target1", "target2"]  
        if cue_side_aud == "left" :
            if target_type == "target1" :
                aud = audio["target1"]["left"]["sound"]
            elif target_type == "target2":
                aud = audio["target2"]["left"]["sound"]
        elif cue_side_aud == "right":
            if target_type == "target1" :
                aud = audio["target1"]["right"]["sound"]
            elif target_type == "target2":
                aud = audio["target2"]["right"]["sound"]

        #trial 
        
        win.flip()
        core.wait(iti) 
        #pull button markers  (these will be added as current trial) 
        iti_presses, raw_presses = pull_responses(hware, run_onset)
        #add false alarms to raw dict 
        append_raw_mp(raw_presses, raw_rpb, run_onset)
        #add false alarms to results dict 
        append_iti_mp(iti_presses, results_per_block, trial)
        #use stim_dur_lsl for RT as well 
        stim_dur_lsl = pylsl.local_clock()  #should return a similar onset time as if using pychopy's local clock 
        aud.play() 
        #check for button press here function should return same as waitKeys ->  "left" or "right", rt, and onset 
        Keys , raw, false_alarms = pull_stim_response(hware, run_onset, stim_dur_lsl, trial_wait_time) 
        #handle raw and false alarms 
        append_raw_mp(raw, raw_rpb, run_onset)
        append_iti_mp(false_alarms, results_per_block, trial)
        
        #if pressed 
        if Keys != None :
            time_left = trial_wait_time - get_time(stim_dur_lsl) 
            key_pressed = Keys[0]
            correct = int(key_pressed == cue_side_aud)
            stimuli.feedback_flip(win, params, hware, correct, cue_side_vis, time_left_in_trial = None) #changed back to none as found this not helpful 
            onset = Keys[1]
            rt = Keys[2]
            
            time_left = trial_wait_time - get_time(stim_dur_lsl) 
            if time_left > 0 :  #recheck in case near edge case 
                #wait for stim to be over 
                core.wait(time_left) #in case it is longer than anticipated
    
        #if not pressed 
        elif Keys == None : 
            onset = None 
            correct = 0
            key_pressed = None
            rt = None
            stimuli.feedback_flip(win, params, hware, 0, cue_side_vis, time_left_in_trial = None) 
        
        #INCENTIVE Calculation: calculated but not added to results 
        this_t_tally = _correct_Keys(key_pressed, cue_side_aud) #returns how much money added or subtracted
        tally += this_t_tally
#       trial["this_trial_tally"] = this_t_tally #[10:12PM 10-20-26 @aditirj2] Commented out of results as incentive is not being used 
#       trial["total_tally"] = tally 
        
        #add correct computation for any trial (d_type alr accounted for in predetermined) 
        trial["button_p_onset"] = onset
        trial["key_pressed"] = key_pressed
        trial["correct"] = correct #boolean value 
        # ONLY FOR MARKER PRESS IN TRIAL RT window 
        trial["stim_start"] = stim_dur_lsl - run_onset
        trial["rt"] = rt 
        
        results_per_block.append(trial) 
    
    return results_per_block , tally , raw_rpb



