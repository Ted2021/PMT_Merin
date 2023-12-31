from art import *
import sys
import os
from drs4 import *
from filterwheel import *
from TuneLit import *
from agilent33250a import *
from generalfunc import *
import subprocess
import datetime
#import uproot
from Merin import PMT_Merin_sys
import threading
import time

def GetToday():
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        Y = now.strftime('%Y%m%d')
        #y = now.strftime('%y%m%d')
        #print(d) 
        return Y


def DoubleHVGainMeasurement(type, hv, pmt_tar, pmt_ref, lit, timing = 0):
        
        if type == "Single":
            file_name_tar = GetToday() + "_" + pmt_tar + "_" + "single" + "_" + "{0}V".format(hv) + ".root"
            file_name_ref = GetToday() + "_" + pmt_ref + "_" + "single" + "_" + "{0}V".format(hv) + ".root"
        elif type == "Multi":
            file_name_tar = GetToday() + "_" + pmt_tar + "_" + "multi" + "_" + "{0}V".format(hv) + ".root"
            file_name_ref = GetToday() + "_" + pmt_ref + "_" + "multi" + "_" + "{0}V".format(hv) + ".root"
        elif type == "Ap":
            file_name_tar = GetToday() + "_" + pmt_tar + "_" + "AP" + "_" + "{0}-{1}us".format(timing,timing+1) +"_" + "{0}V".format(hv) + ".root"
            file_name_ref = GetToday() + "_" + pmt_ref + "_" + "AP" + "_" + "{0}-{1}us".format(timing,timing+1) +"_" + "{0}V".format(hv) + ".root"


        #トリガーを切る
        Output_off()
        ChangeFW("log.log", lit)
        if lit == 36:
             tree = "dark"
             eve = 1000
        else:
             tree = "source"
             eve = 50000

        if type == "Single" or type == "Multi":
             f = 5.0
             d = 0.0
             ChangeDelay_Manual(80e-9)
             max = "200"
        elif type == "Ap":
             f = 1.0
             d = 850.0
             t_list = [0.0, 0.95e-6, 1.85e-6, 2.75e-6, 3.65e-5]
             dtime = t_list[timing]
             ChangeDelay_Manual(dtime)
             max = "1000"

        def Tar():
            RunHageFusaScript2("log.log", file_name_tar, tree, eve, serial=2317, index = 0,delay = d, freq=f)
        def Ref():
            RunHageFusaScript2("log.log", file_name_ref, tree, eve, serial=2385, index = 1,delay = d, freq=f)

        t1 = threading.Thread(target=Tar)
        t2 = threading.Thread(target=Ref)
        t3 = threading.Thread(target=Output_on)
        t1.start()
        t2.start()
        time.sleep(1)
        t3.start()
        t1.join()
        t2.join()
        t3.join()

        Output_off()

        if tree == "source":
            run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
            subprocess.run(["ipython", run_file, file_name_tar, "Treesource_0", "wform1-wform0", str(50000), pmt_tar + "_" + type + "_" + str(timing) + "_" + "{0}V".format(hv)+".pdf", max])
            subprocess.run(["open", pmt_tar + "_" + type + "_" + str(timing) + "_" + "{0}V".format(hv)+".pdf"])

                  
              
        

if __name__ == "__main__":

    args = sys.argv

    p1 = "AA2333"
    p2 = "AA6811"
    lit_s = 27
    lit_m = 18

    if args[1] == "1":
        #print("aq")
        DoubleHVGainMeasurement("Single", 1400, p1, p2, lit_s)
        DoubleHVGainMeasurement("Single", 1400, p1, p2, 36)
        DoubleHVGainMeasurement("Multi", 1400, p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", 1400, p1, p2, 36)
        input("1400V done")
        DoubleHVGainMeasurement("Multi", 1300, p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", 1300, p1, p2, 36)
        input("1300V done")
        DoubleHVGainMeasurement("Multi", 1200, p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", 1200, p1, p2, 36)
        input("1200V done")
        DoubleHVGainMeasurement("Multi", 1100, p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", 1100, p1, p2, 36)
        input("1100V done")
        DoubleHVGainMeasurement("Multi", 1000, p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", 1000, p1, p2, 36)
        input("1000V done")
        DoubleHVGainMeasurement("Multi", "0900", p1, p2, lit_m)
        DoubleHVGainMeasurement("Multi", "0900", p1, p2, 36)

    Nh_t = 1060
    Nh_r = 1040
    lit_Ns = 24
    lit_Nm = 20
    lit_a = 13
    if args[1] == "2":
        DoubleHVGainMeasurement("Single", "NH", p1, p2, lit_Ns)
        DoubleHVGainMeasurement("Single", "NH", p1, p2, 36)
        DoubleHVGainMeasurement("Multi", "NH", p1, p2, lit_Nm)
        DoubleHVGainMeasurement("Multi", "NH", p1, p2, 36)

        for i in range(5):
            DoubleHVGainMeasurement("Ap", "NH", p1, p2, lit_a, timing = i)
            DoubleHVGainMeasurement("Ap", "NH", p1, p2, 36, timing = i)
        #DoubleHVGainMeasurement("Ap", "NH", p1, p2, lit_a, timing = 3)
        #DoubleHVGainMeasurement("Ap", "NH", p1, p2, 36, timing = 3)


