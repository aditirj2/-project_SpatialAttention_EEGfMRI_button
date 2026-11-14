" created by @AditiJindal 9-20-2026" 

# main file that runs task takes from config.py 

import config 
import calibration
import instructions 
import predetermined
import dichotic_task 
import stimuli 
import output 
import trigger
from psychopy import visual, core, event, gui, monitors
import hashlib
import random 
import os 
import pandas as pd 
from psychopy.hardware import keyboard, speaker
import pylsl

def test_audio(audio) :
     for i in range(5) :
        
        targets = [audio["target1"]["left"]["sound"], audio["target2"]["left"]["sound"], audio["target1"]["right"]["sound"], audio["target2"]["right"]["sound"]]
        names = ["target1L", "target2L", "target1R", "target2R"] 
        single_pick = random.choice(targets) 
        position = targets.index(single_pick) 
        print(names[position]) 
        single_pick.play() 
        core.wait(3) 
    
def test_itis() :
     for i in range(20) : 
        session = predetermined.trials_per_block(participant_id, audio, config.params, SNR) #saves session as tuple: each is one block order is either fixed or random 
        check = predetermined.check_session_ITIs(session) #print this block to check 
        ITIs, total_itis = predetermined.check_session_ITIs(session) 
        print(f"total itis: {total_itis}")
        #csv 
        df = output.dict_to_df(ITIs)
        df.to_csv(config.DATA_PATH/ f"{i} output_ITIs.csv", index=True)

def trial_ord(order):
    
    order_to_blocks = []
    pairs = {"1": "AttR", "2": "AttL", "3": "AttND"}
    
    for i in order: #need to make sure iterates over each int value 
        order_to_blocks.append(pairs[i])
    
    return order_to_blocks


ID_OFFSET = 1_000_000   # converted (non-numeric) IDs land above this so they rarely clash with real IDs
ID_RANGE = 10**8

def get_participant_id() :
    """Show a setup GUI and return the participant ID changed to int, raw id, and order.
    Whole non-negative number -> used as typed ("089" -> 89).
    Anything else (letters, "5.0", "-3", ...) -> converted to a deterministic int
    via SHA-256 (same text always gives the same int; Python's hash() is salted per run).
    Empty -> asks again. Cancel -> quits cleanly."""
    
    err_msg = "" 
    while True :
        dlg = gui.Dlg(title="Participant Setup") #builds box 
        dlg.addText("Participant info")
        dlg.addField("Participant ID (whole number, e.g. 1):", "") #builds singular input 
        dlg.addText("Order info")
        dlg.addField("Order (whole number, e.g. 123, 321, 213):", "") #builds singular input 
        dlg.addText(err_msg)  #only shows if err occurs 
        dlg.show()
        
        if not dlg.OK :
            print("setup cancelled")  #handles quitting 
            core.quit()
        raw = str(dlg.data[0]).strip() 
        
        #handles spaces  
        order = str(dlg.data[1])
        order = order.replace(" ", "") #removes any spaces inside as well as outside 
        
        if sorted(order) != ["1", "2", "3"] :
            err_msg = "WRONG ORDER. Order must use 1, 2, 3 once each" 
            continue 
        if raw == "" :
            err_msg = "" #reset err 
            continue #jumps back to top of loop 
        try :
            pid = int(raw)
            if pid >= 0 :
                return raw, pid, order #will be same if pid == int > 0 
        except ValueError :
            pass
        pid = ID_OFFSET + int(hashlib.sha256(raw.encode("utf-8")).hexdigest(), 16) % ID_RANGE
        print(f"'{raw}' is not a whole number -> converted to participant_id {pid}") #add raw "ID into the results doc" 
        return raw, pid, order 

def get_session_mode():
    while True:
        dlg = gui.Dlg(title="Session mode")
        dlg.addField("Mode:", choices=["Full session", "Manual"])
        dlg.show()
        if not dlg.OK:
            print("setup cancelled")  #handles quitting 
            core.quit()                      # same cancel handling as before
        mode = dlg.data[0]           # what type is this? a string
        break

    if mode == "Full session":
        max_cal = None
        per_block = None
        return max_cal, per_block               # what should "no changes" return? nothing to change so none  

   #box 2 appears only if manual pressed 
    err_msg = ""                     # same pattern as the order field
    while True:
        dlg = gui.Dlg(title="Manual settings")
        dlg.addField("Max calibration trials:", "")
        dlg.addField("Trials per block:", "")
        dlg.addText(err_msg)
        dlg.show()
        if not dlg.OK:
            print("setup cancelled")  #handles quitting 
            core.quit()   # cancel 'handling
            
        raw_max_cal =  dlg.data[0]
        raw_per_block = dlg.data[1]
        
        try :
            max_cal = int(raw_max_cal)
            per_block = int(raw_per_block)
        except ValueError :
            err_msg = "both values must be integers" 
            continue 
        if max_cal <= 0 or per_block <= 0 :
            err_msg = "both values must be greater than 0"
            continue 
        
        return max_cal, per_block


def main() : 
    
    # [IMPORTANT] Monitor that we are gonna use (e.g StimPCmonitor)
    config.hware['mon'] = monitors.Monitor('LAPTOP-5HF1DC3K') #'StimPCmonitor'
    # import button as inlet
    config.hware['button']  = trigger.importPylsl()  #importPy returns inlet stream and stores in config.button 
    config.hware['keyboard'] = keyboard.Keyboard()
    config.hware['speaker']  = speaker.SpeakerDevice(resample=True) # 0 is headphones, 2 is external speaker

    #results list -> in BIDs look for later 
    results = []
    raw_results = []
    
    #GUI: ask for participant ID 
    print("asking for participant ID") 
    raw_id, participant_id, order = get_participant_id() 
    config.params["conditions"] = trial_ord(order) #changes global variable; always resets in whenever main.py is run
    
    #GUI: change max trial calibration and number of trials 
    max_cal, per_block = get_session_mode()
    
    if max_cal != None:
        calibration.MAX_TOTAL_TRIALS = max_cal #changes global variable; always resets in whenever main.py is run
    if per_block != None:
        config.params["trials_per_block"] = per_block #changes global variable; always resets in whenever main.py is run
    
    print(f"Session params : maximum calibration trials : {max_cal}; trials per block : {per_block}") 
    print(f"Hardcoded params (for checking) -> Session params : maximum calibration trials : {calibration.MAX_TOTAL_TRIALS}; trials per block : {config.params['trials_per_block']}")
    
    # one folder per participant: data/participant089/
    participant_dir = config.DATA_PATH / f"{raw_id}" #save folder with raw_id name... what you need to plug in anyways 
    participant_dir.mkdir(parents=True, exist_ok=True)
    
    def end_experiment():    
        #savecsv
        #turn results into csv for export 
        try: 
            df = output.dict_to_df(results)
            df.to_csv(participant_dir / f"participant{participant_id:03d}-TERMINATED_TRIAL-output.csv", index=True)
        except : 
            print("Shutdown ERROR: could not save CSV") 
        #end stream 
        try : 
            trigger.turnStreamOff(config.hware['button'])
        except : 
            print("Shutdown Error: Could not close stream") 
        # Force the Python process to terminate immediately
        os._exit(0) 
    
    print("running dichotic auditory task")
    # Add a global key 'esc' to trigger the function
    event.globalKeys.add(key=config.hware["keys"]["quit_key"], func=end_experiment)

    # Initialize Window 
    win = visual.Window(monitor=config.hware['mon'], size=config.hware["aditimon_size"], infoMsg='', color=config.scr["darkgrey"], fullscr=True)
    
    # Fixation Cross object stim
    fixwin = visual.TextStim(win, text="+", height=0.1, color=config.scr["white"])
    
    #run calibration.py
    print("running calibration")  
    SNR = calibration.staircase(win, config.params, config.hware, pylsl.local_clock()) #loads audio twice... is redundant; fix later 
    print(f"calibration complete SNR: {SNR}") 
    
    #load audio 
    print("loading audio") 
    audio = stimuli.load_sound(config.SCANNER_NOISE_PATH, config.target1_path , config.target2_path , config.params["default_sample_rate"], SNR) 
    
    #run predetermined.py returns 3 separate lists 
    print("running predetermined.py") 
    #add ses_order asw 
    session = predetermined.trials_per_block(participant_id, audio, config.params, SNR, raw_id) #saves session as tuple: each is one block order is either fixed or random 
    
    #start background audio noise 
    audio["noise"]["sound"].play(loops=30) # HARDCODED LOOP should loop until end if 5 minutes for audio and then 60 minute run approx -> 150 total mins run time for audio
    print("about to draw")
    
    #instruction screen
    instructions.starting_instructions(win, config.params, config.hware) 
    
    running_tally = 0  #[10:11 PM aditirj2 10-20-2026] EDIT: counts the tally, but will not display it as it is commented out for now 
    summary_rows = [] 
    t0_lsl = pylsl.local_clock() #returns start time on lsl clock 
    
    for i, block in enumerate(session): 
            
        print(f"session:{i}")
        results_per_block , tally, raw = dichotic_task.dichotic_task_block(win, block, audio, config.params, config.hware, SNR, t0_lsl, running_tally)
        
        
        #post data collection results #TODO -> turn into a separate file later 
        block_prop_correct = sum(trial["correct"] for trial in results_per_block) / config.params["trials_per_block"] #@aditirj2 [10-30-2026] changed
        
        summary_rows.append({
            "raw_id": raw_id,
            "participant_id": participant_id,
            "st_raw_lsl": t0_lsl,
            "SNR": SNR,
            "block_number": i + 1,
            "condition": block[0]["condition"],
            "block_prop_correct": block_prop_correct,
        })
        
        results.append(results_per_block)
        raw_results.append(raw) 
        running_tally = tally

        if i != (len(session)-1) : 
            #print update screen after one block with new tally 
            print(f"block {i} Done! Instructor must press SPACE on Keyboard to continue")
            instructions.update_instructions(win, config.params, config.hware, running_tally) 
            #rest period ( if neccessary) : set to 0.0 for now 
            core.wait(config.params["inter-block_wait_time"]) 
    
    #end screen 
    print("Experiment Complete! Instructor must press SPACE to end run. Output CSV will be saved in data/patientid")
    instructions.end_instructions(win, config.params, config.hware, running_tally) 
    
    #turn results into csv for export in BIDs format 
    df_summary = pd.DataFrame(summary_rows)
    df_results = output.dict_to_df(results)
    df_raw_results = output.dict_to_df(raw_results)
    df_results.to_csv(participant_dir / f"participant{participant_id:03d}-output.csv", index=True)
    df_raw_results.to_csv(participant_dir / f"participant{participant_id:03d}-RAW_output.csv", index=True)
    df_summary.to_csv(participant_dir / f"participant{participant_id:03d}-SUMMARY.csv", index=True)
    
    #stream close 
    trigger.turnStreamOff(config.hware['button']) 
    
if __name__ == "__main__":  #doens't run this code if imported 
    main()

    
    