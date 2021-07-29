from time import sleep
import serial
import threading
import logging 
import time
import numpy as np
import simpleaudio as sa
import multiprocessing

def metronome(num):
    if  num == 0: 
        metronome_obj = sa.WaveObject.from_wave_file("click.wav")
        play_metronome = metronome_obj.play()
        #play_metronome.wait_done()
    else: 
        metronomeup_obj = sa.WaveObject.from_wave_file("clickup.wav")
        play_metronomeup = metronomeup_obj.play()
        #play_metronomeup.wait_done()

def whitenoise(stop_event):
    noise_obj = sa.WaveObject.from_wave_file("whitenoise_dec.wav")
    play_whitenoise = noise_obj.play()

    while stop_event.is_set():
        play_whitenoise.stop()

def audiofeedback(channel):
    if channel == 'left':
        left_obj = sa.WaveObject.from_wave_file("left.wav")
        play_left = left_obj.play()
        #play_left.wait_done()
    elif channel == 'right':
        right_obj = sa.WaveObject.from_wave_file("right.wav")
        play_right = right_obj.play()
        #play_right.wait_done()

def countdown(beats):
    for i in range(beats):
        print(str(i+1))
        if i == 0:
            #thread_metronome = threading.Thread(target=metronome(1))
            #thread_metronome.start() 
            process_metronome = multiprocessing.Process(target=metronome(1))
            process_metronome.start()
            
        else: 
            #thread_metronome = threading.Thread(target=metronome(0))
            #thread_metronome.start() 
            process_metronome = multiprocessing.Process(target=metronome(0))
            process_metronome.start()
        
        if i+1==beats and mode == EMS:
            if mode_feedback == PGM:
                sleep(time_beats-extensor_preemption) 
                ser.write("2\n".encode()) 
                sleep(extensor_preemption)
                ser.write("2\n".encode()) 
            elif mode_feedback == AUDIO:
                sleep(time_beats-extensor_preemption) 
                #ser.write("2\n".encode()) 
                sleep(extensor_preemption)
                #ser.write("2\n".encode())
        else:
            sleep(time_beats)  

def getInput():
    global flag 
    global current_time
    while 1:
        input = ser.readline(ser.in_waiting)

        if b'HIT_LEFT' in input:
            if(getTime() - current_time  > 0.05):
                logging.info("HIT_LEFT:\t" + str(getTime()))
                current_time = getTime()
        elif b'HIT_RIGHT' in input:
            if(getTime() - current_time  > 0.05):
                logging.info("HIT_RIGHT:\t" + str(getTime()))
                current_time = getTime()
        
        if flag == True:
            break

def PGMcontrol():
    global flag    

    #make thread object for white noise
    thread_kill = threading.Event()
    thread_whitenoise = threading.Thread(target=whitenoise, args=[thread_kill])
    thread_whitenoise.start()
    sleep(2)

    countdown(number_of_beats)
    #exercise('easy', 2)
    exercise(mode_difficulty, mode_number)
    flag = True

    sleep(2)
    thread_kill.set()
    thread_whitenoise.join()

def getTime():
    global start_time
    return time.time() - start_time

def WristControl(channel, time, num, metro_num):       
    if metro_num == 0:
        thread_metronome = threading.Thread(target=metronome(0))
        thread_metronome.start()
        #process_metronome = multiprocessing.Process(target=metronome(0))
        #process_metronome.start()
    else:
        #process_metronome = multiprocessing.Process(target=metronome(1))
        #process_metronome.start()
        thread_metronome = threading.Thread(target=metronome(1))
        thread_metronome.start() 

    for repetation_number in np.arange(num): 
        if channel == 'left':
            if mode_feedback == PGM:
                logging.info("PGM_LEFT:\t" + str(getTime()))
                ser.write("3\n".encode())
                sleep(time * 0.1)
                ser.write("3\n".encode())
                ser.write("4\n".encode())
                sleep(time * 0.2)
                ser.write("4\n".encode())
                sleep(time * 0.7)

            elif mode_feedback == AUDIO:
                #process_left = multiprocessing.Process(target=audiofeedback('left'))
                #process_left.start()
                thread_left = threading.Thread(target=audiofeedback("left"))
                logging.info("AUDIO_LEFT:\t" + str(getTime()))
                thread_left.start()
                sleep(time)

        elif channel == 'right':
            if mode_feedback == PGM:
                logging.info("PGM_RIGHT:\t" + str(getTime()))
                ser.write("1\n".encode())
                sleep(time * 0.1)
                ser.write("1\n".encode())
                ser.write("2\n".encode())
                sleep(time * 0.2)
                ser.write("2\n".encode())
                sleep(time * 0.7)

            elif mode_feedback == AUDIO:
                #process_right = multiprocessing.Process(target=audiofeedback('right'))
                #process_right.start() 
                thread_right = threading.Thread(target=audiofeedback("right"))
                logging.info("AUDIO_RIGHT:\t" + str(getTime()))
                thread_right.start()
                sleep(time)

        elif channel == 'rest':
            sleep(time)        

#
COM_port = 'COM5'
baud_rate = 115200
time_beats = 0.8
extensor_preemption = 0.1
EMS = 1
NO_EMS = 2
PGM = 1
AUDIO = 2

#setup mode
mode = EMS
mode_feedback = int(input("Please enter the mode of feedback(PGM: 1, AUDIO: 2)"))
mode_difficulty = input("Please enter the difficulty(easy, medium or hard): ")
mode_number = int(input("Please enter the exercise No.: "))
number_of_beats = int(input("Please enter the number of beats: "))
#open the connection
ser = serial.Serial(COM_port, baud_rate)#, write_timeout=0,timeout=0) 

#setup flag
flag = False

#setup logging 
FORMAT = '%(message)s'
filename = input("Please enter the username: ")
#file_handler = logging.FileHandler('Pedrotest_ex5_3 .log')
file_handler = logging.FileHandler(filename + "_" + str(mode_feedback) + "_" + mode_difficulty + "_" + str(mode_number) + ".log")
logging.basicConfig(format=FORMAT,level=logging.DEBUG)
file_handler.setFormatter(logging.Formatter(FORMAT))
logging.getLogger().addHandler(file_handler)

#make thread object
start_time = time.time()
current_time = getTime()
thread_input = threading.Thread(target=getInput)
thread_output = threading.Thread(target=PGMcontrol)

thread_input.start()
thread_output.start()

#thread_obj.join()

######################## Exercise Settings ######################## 
def exercise(mode, num):
    rhythm = {
        'easy' : lambda : ex_easy(num),
        'medium' : lambda : ex_medium(num),
        'hard' : lambda : ex_hard(num)
    }
    rhythm[mode]()

def ex_easy(num):
    rhythm_easy = {
        1 : lambda : ex1_easy(),
        2 : lambda : ex2_easy(),
        3 : lambda : ex3_easy(),
        4 : lambda : ex4_easy(),
        5 : lambda : ex5_easy(),
        6 : lambda : ex6_easy(),
        7 : lambda : ex7_easy(),
        8 : lambda : ex8_easy()
    }
    rhythm_easy[num]()

def ex_medium(num):
    rhythm_medium = {
        1 : lambda : ex1_medium(),
        2 : lambda : ex2_medium(),
        3 : lambda : ex3_medium(),
        4 : lambda : ex4_medium(),
        5 : lambda : ex5_medium(),
        6 : lambda : ex6_medium(),
        7 : lambda : ex7_medium(),
        8 : lambda : ex8_medium()
    }
    rhythm_medium[num]()

def ex_hard(num):
    rhythm_hard = {
        1 : lambda : ex1_hard(),
        2 : lambda : ex2_hard(),
        3 : lambda : ex3_hard(),
        4 : lambda : ex4_hard(),
        5 : lambda : ex5_hard(),
        6 : lambda : ex6_hard(),
        7 : lambda : ex7_hard(),
        8 : lambda : ex8_hard()
    }
    rhythm_hard[num]()

############ easy ############
def ex1_easy():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex2_easy():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex3_easy():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex4_easy():
    time_from_bpm = 0.8
    for i in range(1):
        WristControl('right', time_from_bpm, 1, 1)
        WristControl('left', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)
        WristControl('right', time_from_bpm, 1, 0)

        WristControl('left', time_from_bpm, 1, 1) 
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)

def ex5_easy():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0) 
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0) 
    WristControl('left', time_from_bpm, 1, 0)   

def ex6_easy():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex7_easy():
    time_from_bpm = 0.8
    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

def ex8_easy():
    time_from_bpm = 0.8
    WristControl('left', time_from_bpm, 1, 1)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
############ medium ############
def ex1_medium():
    time_from_bpm = 0.8
    for i in range(2):
        WristControl('right', time_from_bpm, 1, 1)
        WristControl('left', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)
    for j in range(2):
        WristControl('right', time_from_bpm, 1, 1)
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)

def ex2_medium():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    
    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex3_medium():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    
    WristControl('left', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex4_medium():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

def ex5_medium():
    time_from_bpm = 0.8
    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

def ex6_medium():
    time_from_bpm = 0.8
    for i in range(1):
        WristControl('right', time_from_bpm, 1, 1)
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('rest', time_from_bpm, 1, 0)
        WristControl('left', time_from_bpm, 1, 0)

        WristControl('left', time_from_bpm, 1, 1)
        WristControl('left', time_from_bpm, 1, 0)
        WristControl('rest', time_from_bpm, 1, 0)
        WristControl('right', time_from_bpm, 1, 0)

def ex7_medium():
    time_from_bpm = 1.6
    
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm / 2, 2, 1)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('left', time_from_bpm / 2, 2, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)

    WristControl('right', time_from_bpm / 2, 2, 1)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('left', time_from_bpm / 2, 2, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)

def ex8_medium():
    time_from_bpm = 1.6
    
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm / 2, 2, 1)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('right', time_from_bpm / 2, 2, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm / 2, 2, 1)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('left', time_from_bpm / 2, 2, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)

############ hard ############
def ex1_hard():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
     
def ex2_hard():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex3_hard():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

    WristControl('left', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex4_hard():
    time_from_bpm = 0.8
    WristControl('rest', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)

def ex5_hard():
    time_from_bpm = 0.8
    WristControl('rest', time_from_bpm, 1, 1)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('right', time_from_bpm, 1, 0)

def ex6_hard():
    time_from_bpm = 0.8
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    
    WristControl('right', time_from_bpm, 1, 1)
    WristControl('left', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)
    WristControl('rest', time_from_bpm, 1, 0)

    WristControl('right', time_from_bpm / 2, 1, 1)
    WristControl('left', time_from_bpm / 2, 1, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('right', time_from_bpm / 2, 1, 1)
    WristControl('left', time_from_bpm / 2, 1, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)

    WristControl('right', time_from_bpm / 2, 1, 1)
    WristControl('left', time_from_bpm / 2, 1, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    WristControl('right', time_from_bpm / 2, 1, 1)
    WristControl('left', time_from_bpm / 2, 1, 0)
    WristControl('rest', time_from_bpm / 2, 2, 0)
    
def ex7_hard():
    time_from_bpm = 0.8
    for i in range(1):
        WristControl('left', time_from_bpm, 1, 1)
        WristControl('right', time_from_bpm, 1, 0)
        WristControl('rest', time_from_bpm, 1, 0)
        WristControl('rest', time_from_bpm, 1, 0)

        WristControl('left', time_from_bpm / 2, 1, 1)
        WristControl('right', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 2, 0)
        WristControl('left', time_from_bpm / 2, 1, 1)
        WristControl('right', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 2, 0)

def ex8_hard():
    time_from_bpm = 1.6
    for i in range(1):
        WristControl('rest', time_from_bpm / 2, 1, 1)
        WristControl('right', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 1, 0)
        WristControl('left', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 1, 0)

    for j in range(1):
        WristControl('rest', time_from_bpm / 2, 1, 1)
        WristControl('right', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 1, 0)
        WristControl('left', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 1, 0)
        WristControl('right', time_from_bpm / 2, 1, 0)
        WristControl('rest', time_from_bpm / 2, 1, 0)
        WristControl('left', time_from_bpm / 2, 1, 0)


def ex1():
    # repeat beat (quarter note)
    for i in range(64):
        WristControl('right', 0.8, 1, 0)

def ex2():
    # Single stroke four
    for i in range(4):
        WristControl('right', 0.8, 1, 1)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
         
        WristControl('left', 0.8, 1, 1)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)

def ex3():
    # Single paradiddle
    for i in range(8):
        WristControl('right', 0.8, 1, 1)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)
        
        WristControl('left', 0.8, 1, 1)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)

def ex4():
    # double paradiddle
    for i in range(5):
        WristControl('right', 0.8, 1, 1)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        
        WristControl('right', 0.8, 1, 1)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)

        WristControl('left', 0.8, 1, 1)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)

def ex5():
    # double paradiddle
    for i in range(6):
        WristControl('right', 0.4, 2, 1)
        WristControl('left', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)
        WristControl('right', 0.8, 1, 0)

        WristControl('left', 0.4, 2, 1)
        WristControl('right', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
        WristControl('left', 0.8, 1, 0)
