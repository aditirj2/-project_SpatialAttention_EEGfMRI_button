"""SWITCH in-scanner task — LSL trigger / button-box helpers (EEG-fMRI).

Converted to Python from the original MATLAB-based task code by Leykza.
"""
# Try different import approaches for pylsl
import pylsl
from pylsl import StreamInlet
from psychopy import gui, core 

def importPylsl():

    while True: #loop forever 
        try :
            print("Looking for LSL streams of type 'Markers'...")
            #streams is a list of stream descriptions NOT data 
            streams = pylsl.resolve_byprop('type', 'Markers', timeout=5.0) #searches netowrk for streams with type 'Markers' waiting up to 5 sec
            stream = streams[0].name()
            break 
        except IndexError : 
            dlg = gui.Dlg(title="ERROR: Marker Stream (Button Box) Not Found") #builds box 
            dlg.addText("Press OK to Retry. Cancel to terminate")
            dlg.show() 
            if dlg.OK:
                continue 
            else: 
                print("program terminated")  #handles quitting 
                core.quit()   # cancel handling; no need to "end experiment" as this function is called early on. core quit is fine 

    print(f"Stream found: {stream}") #first stream name -> raise index error here 
    #marker timestamps arrive in computer's LSL clock time  
    inlet = StreamInlet(streams[0], processing_flags=1) #streaminlet connects to streams[0]. processing flags turns on clock synchronization 
    
    return inlet 
    
# Pull incoming markers
def pullMarkers(hware):
    
    #sample: list of markers
    #timestamp : time -> float 
    sample, timestamp = hware['button'].pull_chunk() #hware['button'] stores inlet pull chunk returns all marker presses currently 
    hware['button'].flush() #flushes current marker presses 
    return sample, timestamp
    
def turnStreamOff(inlet):  #check if there is a stream in the first place within function 
    
    inlet.flush()
    inlet.close_stream() #stops recieving streams 
    
    
