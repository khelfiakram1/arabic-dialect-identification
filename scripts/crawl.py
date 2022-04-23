#! /usr/bin/env python

# Tested with Python 3.6.5
# youtube-dl --version 2019.04.30
# sox:      SoX v14.4.1
#ffmpeg version 2.8.15-0ubuntu0.16.04.1

##
# This script shows how to crawl the ADI17 audio files.
# You may need to run the script few times as sometime youtube blocks crawling
##

import subprocess
import os
import time, sys
import threading
youtubeIDList=sys.argv[1]

if not os.path.exists('wav'): os.mkdir('wav')
i=286
f = open(youtubeIDList,"r")

class progress_bar_loading(threading.Thread):

    def run(self):
            global stop
            global kill
            print ('Loading....  ',)
            sys.stdout.flush()
            i = 0
            while stop != True:
                    if (i%4) == 0:
                        sys.stdout.write('\b/')
                    elif (i%4) == 1:
                        sys.stdout.write('\b-')
                    elif (i%4) == 2:
                        sys.stdout.write('\b\\')
                    elif (i%4) == 3:
                        sys.stdout.write('\b|')

                    sys.stdout.flush()
                    time.sleep(0.2)
                    i+=1

            if kill == True:
                print ('\b\b\b\b ABORT!',)
            else:
                print ('\b\b\b done!',)


kill = False
stop = False
p = progress_bar_loading()
p.start()

try:
    #anything you want to run.
    for line in f:
        i=i-1
        print("restant ",i)
        subFolder = './wav/' + str(line.split()[1])
        youtubeID = str(line.split()[0])
        if not os.path.exists(subFolder): os.mkdir(subFolder)
        audioFile = subFolder + '/' + youtubeID + '.wav'
        if os.path.exists(audioFile):
            print("Exist: ", audioFile)
            continue
        print("Processing: ", audioFile, youtubeID)
        process = subprocess.run(['yt-dlp', '-f', '[ext=mp4]', '--output', 'tmp.mp4', "--", str(youtubeID)],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("a")
        #for line in process.stdout:
        #    print(line)
        process = subprocess.run(['ffmpeg', '-i', 'tmp.mp4', 'tmp.wav'], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True)
        #for line in process.stdout:
        #    print(line)
        print('b')
        subprocess.run(['sox', 'tmp.wav', '-r', '16000', '-c', '1', str(audioFile)], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, universal_newlines=True)
        print('c')
        if os.path.exists("tmp.mp4"): os.remove("tmp.mp4")
        if os.path.exists("tmp.wav"): os.remove("tmp.wav")
        if os.path.exists(audioFile):
            print("Successed to download: ", line)
        else:
            print("Failed to download: ", line)
        
    time.sleep(1)
    stop = True
except KeyboardInterrupt or EOFError:
         kill = True
         stop = True
