from art import *
import sys
import os
import datetime
#sys.path.append("/Users/cta/kiyomoto_script/PMT_Merin/")
from drs4 import *
from filterwheel import *
from TuneLit import *
from agilent33250a import *
import matplotlib.pyplot as plt
from generalfunc import * 
import subprocess
#import uproot
from Merin import PMT_Merin_sys
import threading
import time

class DoublePMT(PMT_Merin_sys):
    def __init__(self):
        print("Welcome to PMT Double Entry Sys! ※ This is not Eva")
        #self.logfile = "log.log"
        #self.SingleLit = 18
        #self.DarkLit = 36
        ref = PMT_Merin_sys(manual=True)
        
        print("hogehoge")

    def DoubleHVGainMeasurement(self, file_name, file_name2):
        #トリガーを切る
        Output_off()
        ChangeFW(self.logfile, self.SingleLit)

        def Tar():
            RunHageFusaScript2(self.logfile, file_name, "source", 50000, 2386, 0)
        def Ref():
            RunHageFusaScript2(self.logfile, file_name2, "source", 50000, 2385, 1)

        t1 = threading.Thread(target=Tar)
        t2 = threading.Thread(target=Ref)
        t3 = threading.Thread(target=Output_on)
        t1.start()
        t2.start()
        time.sleep(3)
        t3.start()
        t1.join()
        t2.join()
        t3.join()
        run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
        subprocess.run(["ipython", run_file, file_name, "Treesource_0", "wform1-wform0", str(self.event_s), multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv)])
        subprocess.run(["open", multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv) + ".pdf"])
        
        Output_off()
        ChangeFW(self.logfile, self.DarkLit)

        def Tar_dark():
            RunHageFusaScript2(self.logfile, file_name, "dark", 1000, 2386, 0, 0.0, 5.0)
        def Ref_dark():
            RunHageFusaScript2(self.logfile, file_name, "dark", 1000, 2385, 1, 0.0, 5.0)

        t1 = threading.Thread(target=Tar_dark)
        t2 = threading.Thread(target=Ref_dark)
        t3 = threading.Thread(target=Output_on)
        t1.start()
        t2.start()
        time.sleep(3)
        t3.start()
        t1.join()
        t2.join()
        t3.join()

        Output_off()
        

