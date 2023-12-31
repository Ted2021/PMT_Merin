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


class DoubleEntry:
    def __init__(self, tar, ref):
        self.pmt_tar = tar
        self.pmt_ref = ref
        self.date = self.GetToday()

        #self.Makedir()

        self.hv = 1400
        self.timing = 0

        self.SetFname()

    def SetFname(self):
        self.file_name_tar_s = self.date + "_" + self.pmt_tar + "_" + "single" + "_" + "{0}V".format(self.hv) + ".root"
        self.file_name_ref_s = self.date + "_" + self.pmt_ref + "_" + "single" + "_" + "{0}V".format(self.hv) + ".root"
        self.file_name_tar_m = self.date + "_" + self.pmt_tar + "_" + "multi" + "_" + "{0}V".format(self.hv) + ".root"
        self.file_name_ref_m = self.date + "_" + self.pmt_ref + "_" + "multi" + "_" + "{0}V".format(self.hv) + ".root"
        self.file_name_tar_a = self.date + "_" + self.pmt_tar + "_" + "AP" + "_" + "{0}-{1}us".format(self.timing,self.timing+1) +"_" + "{0}V".format(self.hv) + ".root"
        self.file_name_ref_a = self.date + "_" + self.pmt_ref + "_" + "AP" + "_" + "{0}-{1}us".format(self.timing,self.timing+1) +"_" + "{0}V".format(self.hv) + ".root"

    def GetToday(self):
            t_delta = datetime.timedelta(hours=9)
            JST = datetime.timezone(t_delta, 'JST')
            now = datetime.datetime.now(JST)
            Y = now.strftime('%Y%m%d')
            #y = now.strftime('%y%m%d')
            #print(d) 
            return Y


    def Makedir(self):
        os.makedirs("./analysis/{0}/SinglePhe/".format(self.pmt_tar))
        os.makedirs("./analysis/{0}/SinglePhe/".format(self.pmt_ref))
        for i in range(1400, 800, -100):
            os.makedirs("./analysis/{0}/MultiPhe/{1}V/".format(self.pmt_tar, "{0}".format(i).zfill(4)))
            os.makedirs("./analysis/{0}/MultiPhe/{1}V/".format(self.pmt_ref, "{0}".format(i).zfill(4)))


    def Analysis(self,type, pmt,hv):
        if type == "Single":
            pyfile = "/Users/cta/kiyomoto_script/PMT_analysis/Script/Sample_single.py"
            if pmt == "tar":
                file = self.file_name_tar_s
                ana_dir = "./analysis/{0}/SinglePhe/".format(self.pmt_tar)
                log = "ana_tarpmt.log"
            if pmt == "ref":
                file = self.file_name_ref_s
                ana_dir = "./analysis/{0}/SinglePhe/".format(self.pmt_ref)
                log = "ana_refpmt.log"
        elif type == "Multi":
            pyfile = "/Users/cta/kiyomoto_script/PMT_analysis/Script/Sample_multi.py"
            if pmt == "tar":
                file = self.date + "_" + self.pmt_tar + "_" + "multi" + "_" + "{0}V".format(hv) + ".root"
                ana_dir = "./analysis/{0}/MultiPhe/{1}V/".format(self.pmt_tar, hv)
                log = "ana_tarpmt.log"
            if pmt == "ref":
                file = self.date + "_" + self.pmt_ref + "_" + "multi" + "_" + "{0}V".format(hv) + ".root"
                ana_dir = "./analysis/{0}/MultiPhe/{1}V/".format(self.pmt_ref, hv)
                log = "ana_refpmt.log"

        try:
            with open(log, "a") as fp:
                subprocess.call(["ipython", pyfile, file, ana_dir, "0"], stdout=fp)
                subprocess.call(["ipython", pyfile, file, ana_dir, "1"], stdout=fp)
                print(Color.GREEN + pmt + "_" + type+" ({0}) analysis Done!".format(hv)  + Color.RESET)
        except:
            print("analysis_miss!")


    def DoubleHVGainMeasurement(self, type, lit):

            #トリガーを切る
            Output_off()
            ChangeFW("log.log", lit)
            if lit == 36:
                tree = "dark"
                eve = 1000
            else:
                tree = "source"
                eve = 50000

            if type == "Single":
                f = 5.0
                d = 0.0
                ChangeDelay_Manual(80e-9)
                max = "200"
                file_name_tar = self.file_name_tar_s
                file_name_ref = self.file_name_ref_s

            elif type == "Multi":
                f = 5.0
                d = 0.0
                ChangeDelay_Manual(80e-9)
                max = "200"
                file_name_tar = self.file_name_tar_m
                file_name_ref = self.file_name_ref_m

            elif type == "Ap":
                f = 1.0
                d = 850.0
                t_list = [0.0, 0.95e-6, 1.85e-6, 2.75e-6, 3.65e-5]
                dtime = t_list[self.timing]
                ChangeDelay_Manual(dtime)
                max = "1000"
                file_name_tar = self.file_name_tar_a
                file_name_ref = self.file_name_ref_a


            def Tar():
                RunHageFusaScript2("measure_tarpmt.log", file_name_tar, tree, eve, serial=2317, index = 1,delay = d, freq=f)
            def Ref():
                RunHageFusaScript2("measure_refpmt.log", file_name_ref, tree, eve, serial=2385, index = 0,delay = d, freq=f)

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
                subprocess.run(["ipython", run_file, file_name_tar, "Treesource_0", "wform1-wform0", str(50000), self.pmt_tar + "_" + type + "_" + str(self.timing) + "_" + "{0}V".format(self.hv)+".pdf", max])
                subprocess.run(["open", self.pmt_tar + "_" + type + "_" + str(self.timing) + "_" + "{0}V".format(self.hv)+".pdf"])


                  
              
        

if __name__ == "__main__":

    args = sys.argv

    p1 = "AA2368"
    p2 = "AA6811"
    lit_s = 27
    lit_m = 18

    ana = DoubleEntry(p1, p2)

    if args[1] == "0":
        ana.Makedir()

    if args[1] == "1":
        ana.hv = 1400
        ana.SetFname()
        ana.DoubleHVGainMeasurement("Single", lit_s)
        ana.DoubleHVGainMeasurement("Single", 36)

        for i in range(1400, 800, -100):
            if i == 900:
                ana.hv = "0900"
            else:
                ana.hv = i
            
            #print(ana.hv)
            ana.SetFname()

            thread1 = threading.Thread(target=ana.DoubleHVGainMeasurement, args=("Multi", lit_m))

            def Run_Anascript():
                if ana.hv == 1400:
                    ana.Analysis("Single", "tar",1400)
                    ana.Analysis("Single", "ref",1400)
                else:
                    ana.Analysis("Multi", "tar",int(ana.hv)+100)
                    ana.Analysis("Multi", "ref",int(ana.hv)+100)

            thread2 = threading.Thread(target=Run_Anascript)
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()

            ana.DoubleHVGainMeasurement("Multi", 36)
            input("{0}V done".format(i))

        ana.Analysis("Multi", "tar","0900")
        ana.Analysis("Multi", "ref","0900")

    if args[1] == "3":
        subprocess.call(["ipython", "/Users/cta/kiyomoto_script/PMT_analysis/Script/Sample_HV.py", p1, p1, ana.date.split("20")[-1]])
        subprocess.call(["ipython", "/Users/cta/kiyomoto_script/PMT_analysis/Script/Sample_HV.py", p1, p2, ana.date.split("20")[-1]])

    Nh_t = 1120
    Nh_r = 1040
    lit_Ns = 24
    lit_Nm = 20
    lit_a = 13
    if args[1] == "2":
        ana.hv = Nh_t
        ana.SetFname()
        ana.DoubleHVGainMeasurement("Single", lit_Ns)
        ana.DoubleHVGainMeasurement("Single", 36)
        ana.DoubleHVGainMeasurement("Multi", lit_Nm)
        ana.DoubleHVGainMeasurement("Multi", 36)

        for i in range(5):
            ana.timing = i
            ana.SetFname()
            ana.DoubleHVGainMeasurement("Ap", lit_a)
            ana.DoubleHVGainMeasurement("Ap", 36)
        #DoubleHVGainMeasurement("Ap", "NH", p1, p2, lit_a, timing = 3)
        #DoubleHVGainMeasurement("Ap", "NH", p1, p2, 36, timing = 3)


