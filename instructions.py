from psychopy import visual, core, event
import config 


#starting screen instructions : include win.flip() in this function 
def _build_instructions_text(params, hware):
    reward = params["incentive_value"]
#    key_left = hware["keys"]["detection_key_left"].upper() 
#    key_right = hware["keys"]["detection_key_right"].upper()
    space = hware["keys"]["wait_key"].upper()

    return (
        "Instruction Screen\n\n"
        "Please wait for instructor to begin." 
#        f"Press {space} to begin."
    )

def _start_calibration_text(params, hware) :
    space = hware["keys"]["wait_key"].upper()
    return (
        "Starting Calibration\n"
#        f"Press {space} to begin."
        "Please wait for instructor to begin." 
    )

def _end_calibration_text(params, hware) :
    space = hware["keys"]["wait_key"].upper()
    return (
        "Calibration Complete!\n"
        "Please wait for instructor." 
#        f"Press {space} to continue."
    )

def _build_earnings_text(params, hware, tally_cents):
    total_dollars = tally_cents / 100
    sign = "-" if total_dollars < 0 else ""
    return (
        "Block complete!\n\n"
#        f"Correct detections: {n_hits} (+${reward_cents / 100:.2f})\n"
#        f"False alarms: {n_false_alarms} (-${penalty_cents / 100:.2f})\n\n"
#        f"Total earned: {sign}${abs(total_dollars):.2f}\n\n"
        "Next session starting soon.\n\n"
        "Please wait for instructor." 
    )
    
def _end_experiment(params, hware, tally_cents):
    total_dollars = tally_cents / 100
    sign = "-" if total_dollars < 0 else ""
    return (
        "Experiment complete!\n\n"
#        f"Correct detections: {n_hits} (+${reward_cents / 100:.2f})\n"
#        f"False alarms: {n_false_alarms} (-${penalty_cents / 100:.2f})\n\n"
#        f"Total earned: {sign}${abs(total_dollars):.2f}\n\n"
        "Thank you!"
    )

def starting_instructions(win, params, hware) : 
    print("printing starting instructions")
    starting = visual.TextStim(win, text=_build_instructions_text(params, hware), color=config.scr["white"])
    starting.draw() 
    win.flip() 
    event.waitKeys(keyList = [hware["keys"]["wait_key"]])

def update_instructions(win,params,hware,tally) :
    print(f"printing update instructions... tally = {tally}")
    update = visual.TextStim(win, text=_build_earnings_text(params, hware, tally), color=config.scr["white"])
    update.draw() 
    win.flip() 
    event.waitKeys(keyList = [hware["keys"]["wait_key"]])
    
def end_instructions(win,params,hware,tally) :
    print(f"printing end instructions... tally = {tally}")
    print(f"printing update instructions... tally = {tally}")
    end = visual.TextStim(win, text=_end_experiment(params, hware, tally), color=config.scr["white"])
    end.draw() 
    win.flip() 
    event.waitKeys(keyList = [hware["keys"]["wait_key"]])
    
def starting_calibration_instructions(win, params, hware): 
    print("printing starting calibration instructions")
    starting = visual.TextStim(win, text=_start_calibration_text(params, hware), color=config.scr["white"])
    starting.draw() 
    win.flip() 
    event.waitKeys(keyList = [hware["keys"]["wait_key"]])
    
def end_calibration_instructions(win, params, hware): 
    print("printing end calibration instructions")
    end = visual.TextStim(win, text=_end_calibration_text(params, hware), color=config.scr["white"])
    end.draw() 
    win.flip() 
    event.waitKeys(keyList = [hware["keys"]["wait_key"]])
    

    
    