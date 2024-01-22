from art import *
import csv
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
import csv
import shutil
#import uproot


class PMT_Merin_sys:    
    def __init__(self, debug=False, manual=False):

        #パラメータの初期化
        self.date = "yymmdd"
        self.pmt_serial = "XXXXXX"
        self.Anapath = '/Users/cta/work/dora_data/pmt'
        self.path = "/Users/cta/work/dora_data/pmt/{0}/{1}/".format(self.date, self.pmt_serial)
        self.drs4board = 2386
        self.SingleLit = 28     #SinglePheのFW光量
        self.MultiLit = 11      #MultiPheのFW光量
        self.APLit = 11      #AfterpulseのFW光量
        self.Treename_s = "source"
        self.Treename_d = "dark"
        self.hv = 1400      #HVの初期値は1400で固定
        self.event_s = 50000    #Sourceイベント数
        self.event_d = 1000     #Darkイベント数
        self.event_a = 300000   #Afterpulseイベント数

        self.color1 = Color.BG_DEFAULT
        self.color2 = Color.BG_DEFAULT
        self.color4 = Color.BG_DEFAULT
        self.color7 = Color.BG_DEFAULT
        self.para_color = [Color.BG_DEFAULT,    #HV val
                           Color.BG_DEFAULT,    #Single_Lit
                           Color.BG_DEFAULT,    #Multi_Lit
                           Color.BG_DEFAULT,    #AP_Lit
                           Color.BG_DEFAULT,    #Single_Event
                           Color.BG_DEFAULT,    #Dark_Event
                           Color.BG_DEFAULT]    #AP_Event

        self.logfile = self.path + "log.log"

        #マニュアルモードの有無(マニュアルモードの場合、オブジェクトを全て自分で呼び出す必要がある)
        if manual == False:
            #デバッグモードの有無(デバッグモードの場合、ReadDRS、FilterWheel、Agilentの操作がされない)
            if debug == False:
                self.dummy = False
                self.Call()
            else:
                self.dummy = True
                self.DebugMode()
            
    
    def Call(self):
        Art=text2art("PMT")
        print(Art)

        print("~~~ Welcome to PMT measurement System!! (v0.9) ~~~")
        b = False
        while b == False:
            self.pmt_serial = input("Please input PMT serial number? ")
            print("Your PMT => {0}".format(self.pmt_serial))
            key = input("IS it OK? (y/n) ")
            if key == "y":
                b = True

        self.date = self.GetToday()  #測定日を取得
        self.path = self.CreateDir()    #解析データを格納するディレクトリ
        self.logfile = self.path + "log.txt"    #測定logを格納(DRS4, FW, Triggerの動作logを書く)
        self.CreateCSV()            #測定のセットアップをcsvに毎回dumpする

        #測定を開始する
        mode = self.ShowMode()      
        self.RunMeasurement(mode)

    def DebugMode(self):
        Art=text2art("PMT")
        print(Art)

        print("~~~ Welcome to PMT measurement System!! (v0.9) " + Color.RED + "DEBUG MODE " + Color.RESET +"~~~")
        self.date = "yymmdd"
        self.pmt_serial = "XXXXXX"
        self.path = "/Users/cta/work/dora_data/pmt/{0}/{1}/".format(self.date, self.pmt_serial)
        #target_dir = 'temp'
        shutil.rmtree(self.path)
        os.mkdir(self.path)
        self.logfile = self.path + "log.txt"    #測定logを格納(DRS4, FW, Triggerの動作logを書く)
        self.CreateCSV()            #測定のセットアップをcsvに毎回dumpする

        #測定を開始する
        mode = self.ShowMode()      
        self.RunMeasurement(mode)



    def RunMeasurement(self, key):
        b = False
        while b == False:
            if key == "1":
                #self.Set1PELight()
                self.SinglePheMeasurement()
                self.color1 = Color.BG_GREEN
            elif key == "2":
                self.MultiPheMeasurement()
                self.color2 = Color.BG_GREEN
            elif key == "3":
                print("Function is not READY...")
            elif key == "4":
                self.HVGainMeasurement()
                self.color4 = Color.BG_GREEN
            elif key == "5":
                print("Function is not READY...")
            elif key == "6":
                print("Function is not READY...")
            elif key == "7":
                self.AfterPulseMeasurement()
                #print("Function is not READY...")
                self.color7 = Color.BG_GREEN
            elif key == "8":
                print("Function is not READY...")
            elif key == "c":
                self.Setting()
            elif key == "q":
                print("End Process!!")
                #os._exit(os.EX_OK)
                sys.exit()
            else:
                print(Color.RED+"input is invalid!! please input right key!" + Color.RESET)
            key = self.ShowMode()

    def ShowMode(self):
        print("##############################")
        print("Which items are measured??")
        print(self.color1+"1. SinglePhe"+Color.RESET)
        print(self.color2+"2. MultiPhe"+Color.RESET)
        print("3. Pulse Width"+Color.RESET)
        print(self.color4+"4. HV-Gain Curve"+Color.RESET)
        print("5. Transit Time")
        print("6. Transit Time Spread")
        print(self.color7+"7. Afterpulse"+Color.RESET)
        print("8. Photocathod Dependency")
        print("c. Config")
        print("s. Stay")
        print('q. Exit')
        print("##############################")

        key = input("please enter the mode =>(1~9 or c or q)")
        return key
        
    def GetToday(self):
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        Y = now.strftime('%Y%m%d')
        #y = now.strftime('%y%m%d')
        #print(d) 
        return Y

    def CreateDir(self, item = ''):
        dir_exsist = os.path.exists(self.Anapath+'/{0}/{1}/{2}'.format(self.date.split("20")[-1], self.pmt_serial, item))
        #print(self.Anapath+'/{0}/{1}/'.format(y, self.pmt_serial))
        if dir_exsist == True:
            print("Result Directory is Already Exsists!!")
            Selection("is it OK to continue?(y/n)")
            """
            key = input("is it OK to continue?(y/n)")
            if key == "n":
                sys.exists()
            """
        else:
            os.makedirs(self.Anapath+'/{0}/{1}/{2}'.format(self.date.split("20")[-1], self.pmt_serial, item))

        return self.Anapath+'/{0}/{1}/{2}'.format(self.date.split("20")[-1], self.pmt_serial, item)

    def GetPmtSerial(self):
        print("PMT Serial num => {0}".format(self.pmt_serial))
        return self.pmt_serial

    def Getdynodenum(self):
        if self.pmt_serial.startswith("ZQ"):
            dynode_num = 8
            print("PMT Serial => {0} ({1}dynode PMT)".format(self.pmt_serial, dynode_num))
        elif self.pmt_serial.startswith("AA"):
            dynode_num = 7
            print("PMT Serial => {0} ({1}dynode PMT)".format(self.pmt_serial, dynode_num))
        else:
            dynode_num = "Nan"
        return dynode_num
    
    def SetHV(self):
        print("Setting HV...")
        self.hv = int(input("Please Check Power Supplyer and Enter HV-val ==> "))

    def GetHV(self):
        print("~~~~~ HV setting ~~~~~~")
        print("HV-val : "+self.para_color[0]+"{0}".format(self.hv)+Color.BG_DEFAULT)
        print("~~~~~~~~~~~~~~~~~~~~~~~")


    def SetLit(self, lit, type):
        if type == "s":
            old_val = self.SingleLit
            self.SingleLit = int(lit)          #Sourceの光量
            print("Single_Lit: {0} => {1}".format(old_val, self.SingleLit))
        elif type == "m":
            old_val = self.MultiLit
            self.MultiLit = int(lit)         #Multiの光量
            print("Multi_Lit: {0} => {1}".format(old_val, self.MultiLit))
        elif type == "a":
            old_val = self.APLit
            self.APLit = int(lit)            #Afterpulseの光量
            print("AP_Lit: {0} => {1}".format(old_val, self.APLit))
        else:
            print("error! please input correct val")

    def GetLit(self):
        print("~~~~~ LIT setting ~~~~~~")
        print("Single_Lit : FW "+self.para_color[1]+"{0}".format(self.SingleLit)+Color.BG_DEFAULT)
        print("Multi_Lit : FW "+self.para_color[2]+"{0}".format(self.MultiLit)+Color.BG_DEFAULT)
        print("AfterPulse_Lit : FW "+self.para_color[3]+"{0}".format(self.APLit)+Color.BG_DEFAULT)
        print("~~~~~~~~~~~~~~~~~~~~~~~")

    def SetEvents(self, event_num, type):
        if type == "s":
            old_val = self.event_s
            self.event_s = int(event_num)    #Sourceイベント数
            print("Change Event (Single): {0} => {1}".format(old_val, self.event_s))
        elif type == "d":
            old_val = self.event_d
            self.event_d = int(event_num)       #Darkイベント数
            print("Change Event (Dark): {0} => {1}".format(old_val, self.event_d))
        elif type == "a":
            old_val = self.event_a
            self.event_a = int(event_num)    #Afterpulseイベント数
            print("Change Event (AP): {0} => {1}".format(old_val, self.event_a))
        else:
            print("error! please input correct val")


    def GetEvents(self):
        print("~~~~~ Event num setting ~~~~~~")
        print("Event num (Source) => "+self.para_color[4]+"{0}".format(self.event_s)+Color.BG_DEFAULT)
        print("Event num (Dark) => "+self.para_color[5]+"{0}".format(self.event_d)+Color.BG_DEFAULT)
        print("Event num (AfterPulse) => "+self.para_color[6]+"{0}".format(self.event_a)+Color.BG_DEFAULT)
        print("~~~~~~~~~~~~~~~~~~~~~~~")

    def Setting(self):
        b = False
        while b == False:
            self.GetHV()
            self.GetLit()
            self.GetEvents()
            print("Which parameter do you want to change?")
            print("1. High Voltage")
            print("2. Pulsar Lit")
            print("3. Correct Event Num")
            self.para_color = [Color.BG_DEFAULT for i in range(7)]
            key = input("please enter the mode =>(1~3 or b)")
            if key == "1":
                print(" ")
                self.SetHV()
                self.para_color[0] = Color.BG_BLUE
                print(" ")
            elif key == "2":
                print(" ")
                type = "null"
                while True:
                    if type == "s":
                        self.para_color[1] = Color.BG_BLUE
                        break
                    elif type == "m":
                        self.para_color[2] = Color.BG_BLUE
                        break
                    elif type == "a":
                        self.para_color[3] = Color.BG_BLUE
                        break
                    else:
                        type = input("Select Type (s/m/a) => ")
                num = input("Input FW num (1~36) => ")
                self.SetLit(num, type)
                print(" ")
            elif key == "3":
                print(" ")
                type = "null"
                while True:
                    if type == "s":
                        self.para_color[4] = Color.BG_BLUE
                        break
                    elif type == "d":
                        self.para_color[5] = Color.BG_BLUE
                        break
                    elif type == "a":
                        self.para_color[6] = Color.BG_BLUE
                        break
                    else:
                        type = input("Select Type (s/d/a) => ")
                num = input("Input Event num=> ")
                self.SetEvents(num, type)
                print(" ")
            elif key == "b":
                b = True

    def Set1PELight(self):

        #光量の調整
        flag = False
        while flag == False:
            if self.dummy == False:
                ChangeFW(self.logfile, self.SingleLit)
                RunHageFusaScript(self.logfile, self.path+"temp.root", self.Treename_s, 2000, serial = self.drs4board)
                ChangeFW(self.logfile, 36)
                RunHageFusaScript(self.logfile, self.path+"temp.root", self.Treename_d, self.event_d, serial = self.drs4board)
                counts, rate, avg, max_bin = AnaSingleWF(self.path+"temp.root")
                plt.plot(avg)
                plt.show()
                input("IS it OK?")
                plt.clf()
                plt.close()

                plt.hist(max_bin)
                plt.yscale("log")
                plt.show()
                input("IS it OK?")
                plt.clf()
                plt.close()


                if rate < 0.2:
                    self.SingleLit -= 1
                elif rate > 0.5:
                    self.SingleLit += 1
                else:
                    flag = True
            elif self.dummy == True:
                print(Color.YELLOW+"Skip Measurement!!!"+Color.RESET)
                print("SinglePhe Lit is set to default val")
                flag = True

        #光量調整終了
        print("SinglePhe Lit => {0}".format(self.SingleLit))

    def SinglePheMeasurement(self):
        self.SetHV()
        singlepe_path = self.CreateDir(item = 'SinglePhe_{0}V/'.format(self.hv))
        file_name = self.date + '_' + self.pmt_serial + '_' + 'SinglePhe_{0}V'.format(self.hv) + ".root"

        if self.dummy == False:
            ChangeFW(self.logfile, self.SingleLit)
            RunHageFusaScript2(self.logfile, singlepe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
            ChangeFW(self.logfile, 36)
            RunHageFusaScript2(self.logfile, singlepe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)
            run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
            subprocess.run(["ipython", run_file, singlepe_path+file_name, "Tree"+self.Treename_s+"_0", "wform1-wform0", str(self.event_s), singlepe_path+self.date + '_' + self.pmt_serial + '_' + 'SinglePhe_{0}V'.format(self.hv)])
            subprocess.run(["open", singlepe_path+self.date + '_' + self.pmt_serial + '_' + 'SinglePhe_{0}V'.format(self.hv) + ".pdf"])

        elif self.dummy == True:
                print(Color.YELLOW+"Skip Measurement!!!"+Color.RESET)

        self.WriteCSV("SinglePhe", self.SingleLit, self.hv, file_name, self.self.Treename_s, self.event_s, 5.0, 850, self.drs4board)

    def MultiPheMeasurement(self):
        self.SetHV()
        multipe_path = self.CreateDir(item = 'MultiPhe_{0}V/'.format(self.hv))
        file_name = self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv) + ".root"

        if self.dummy == False:
            ChangeFW(self.logfile, self.MultiLit)
            RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
            ChangeFW(self.logfile, 36)
            RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)
            run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
            subprocess.run(["ipython", run_file, multipe_path+file_name, "Tree"+self.Treename_s+"_0", "wform1-wform0", str(self.event_s), multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv)])
            subprocess.run(["open", multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv) + ".pdf"])
        elif self.dummy == True:
                print(Color.YELLOW+"Skip Measurement!!!"+Color.RESET)

        self.WriteCSV("MultiPhe", self.MultiLit, self.hv, file_name, self.Treename_s, self.event_s, 5.0, 850, self.drs4board)

    def HVGainMeasurement(self):
        multipe_path = self.CreateDir(item = 'HVGainCurve/')
        for hv in range(1400, 800, -100):
            self.hv = hv
            input('{0}V Measurement Start! Please Check Power Supplyer! Continue?=>(y/n) '.format(hv))
            file_name = self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(hv) + ".root"
            if self.dummy == False:
                ChangeFW(self.logfile, self.MultiLit)
                RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
                ChangeFW(self.logfile, 36)
                RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)
                run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
                subprocess.run(["ipython", run_file, multipe_path+file_name, "Tree"+self.Treename_s+"_0", "wform1-wform0", str(self.event_s), multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(hv)])
                subprocess.run(["open", multipe_path+self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(hv) + ".pdf"])
            elif self.dummy == True:
                print(Color.YELLOW+"Skip Measurement!!!"+Color.RESET)

            self.WriteCSV("MultiPhe", self.MultiLit, self.hv, file_name, self.Treename_s, self.event_s, 5.0, 850, self.drs4board)


            print('{0}V Measurement Done!'.format(hv))
        print("End HV-Gain Measurement")

    def AfterPulseMeasurement(self):
        afterpulse_path = self.CreateDir(item = 'Afterpulse/')
        input('AfterPulse Measurement Start! Please connect signal line to Function Generator! Continue?=>(y/n) ')

        timing = [0.0, 0.95e-6, 1.85e-6, 2.75e-6, 3.65e-5]
        for i in range(5):
            file_name = self.date + '_' + self.pmt_serial + '_' + 'Afterpulse_{0}-{1}us'.format(i, i+1) + ".root"
            if self.dummy == False:
                ChangeDelay(timing[i])
                ChangeFW(self.logfile, self.APLit)
                RunHageFusaScript(self.logfile, afterpulse_path+file_name, self.Treename_s, self.evnet_a, serial = self.drs4board, delay = 850.0, freq= 1.0)
                ChangeFW(self.logfile, 36)
                RunHageFusaScript(self.logfile, afterpulse_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board, delay = 850.0, freq= 1.0)
                run_file = "/Users/cta/kiyomoto_script/lst-pmt/root_conv/Figure.py"
                subprocess.run(["ipython", run_file, afterpulse_path+file_name, "Tree"+self.Treename_s+"_0", "wform3-wform2", str(self.event_a), afterpulse_path+self.date + '_' + self.pmt_serial + '_' + 'Afterpulse_{0}-{1}us'.format(i, i+1)])
                subprocess.run(["open", afterpulse_path+self.date + '_' + self.pmt_serial + '_' + 'Afterpulse_{0}-{1}us'.format(i, i+1) + ".pdf"])
            elif self.dummy == True:
                print(Color.YELLOW+"Skip Measurement!!!"+Color.RESET)

            self.WriteCSV("AfterPulse", self.APLit, self.hv, file_name, self.Treename_s, self.event_a, 1.0, timing[i], self.drs4board)

    def CreateCSV(self):
        with open(self.path+"{0}_MeasurementLog.csv".format(self.pmt_serial), 'w') as f:
            writer = csv.writer(f)
            l = ["Contents", "Lit", "HighVol", "File", "Tree", "Events", "Freq", "Delay", "DRS_serial"]
            writer.writerow(l)
    
    def WriteCSV(self, contents, lit, hv, file, tree, event, freq, delay, drs_serial):
        with open(self.path+"{0}_MeasurementLog.csv".format(self.pmt_serial), 'a') as f:
            writer = csv.writer(f)
            l = [contents, lit, hv, file, tree, event, freq, delay, drs_serial]
            writer.writerow(l)
        
    
if __name__ == "__main__":
    args = sys.argv
    hoge = PMT_Merin_sys(args[0], args[1])