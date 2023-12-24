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
#import uproot

class Color:
	BLACK          = '\033[30m'#(文字)黒
	RED            = '\033[31m'#(文字)赤
	GREEN          = '\033[32m'#(文字)緑
	YELLOW         = '\033[33m'#(文字)黄
	BLUE           = '\033[34m'#(文字)青
	MAGENTA        = '\033[35m'#(文字)マゼンタ
	CYAN           = '\033[36m'#(文字)シアン
	WHITE          = '\033[37m'#(文字)白
	COLOR_DEFAULT  = '\033[39m'#文字色をデフォルトに戻す
	BOLD           = '\033[1m'#太字
	UNDERLINE      = '\033[4m'#下線
	INVISIBLE      = '\033[08m'#不可視
	REVERCE        = '\033[07m'#文字色と背景色を反転
	BG_BLACK       = '\033[40m'#(背景)黒
	BG_RED         = '\033[41m'#(背景)赤
	BG_GREEN       = '\033[42m'#(背景)緑
	BG_YELLOW      = '\033[43m'#(背景)黄
	BG_BLUE        = '\033[44m'#(背景)青
	BG_MAGENTA     = '\033[45m'#(背景)マゼンタ
	BG_CYAN        = '\033[46m'#(背景)シアン
	BG_WHITE       = '\033[47m'#(背景)白
	BG_DEFAULT     = '\033[49m'#背景色をデフォルトに戻す
	RESET          = '\033[0m'#全てリセット


class PMT_Merin_sys:    
    def __init__(self):
        #パラメータの初期化
        self.Anapath = '/Users/cta/work/dora_data/pmt'
        self.drs4board = 2386
        self.SingleLit = 28     #SinglePheのFW光量
        self.MultiLit = 11      #MultiPheのFW光量
        self.APLit = 11      #AfterpulseのFW光量
        self.Treename_s = "source"
        self.Treename_d = "dark"
        self.hv = 1400      #HVの初期値は1400で固定
        self.event_s = 50000    #Sourceイベント数
        self.event_d = 1000     #Darkイベント数
        self.evnet_a = 300000   #Afterpulseイベント数


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

        self.date = self.GetToday()[1]
        self.path = self.CreateDir()

        self.logfile = self.path + "log.txt"

        self.Call()
    
    def Call(self):
        mode = self.ShowMode()
        self.RunMeasurement(int(mode))

    def RunMeasurement(self, key):
        if key == 1:
            a = 1
            self.Set1PELight()
            self.SinglePheMeasurement()
        elif key == 2:
            a = 2
            self.MultiPheMeasurement()
        elif key == 3:
            a = 3
            print("Function is not READY...")
        elif key == 4:
            a = 4
            self.HVGainMeasurement()
        elif key == 5:
            a = 5
            print("Function is not READY...")
        elif key == 6:
            a = 6
            print("Function is not READY...")
        elif key == 7:
            a = 7
            self.AfterPulseMeasurement()
            #print("Function is not READY...")
        elif key == 8:
            a = 8
            print("Function is not READY...")
        elif key == "c":
            a = 10
            print("Function is not READY...")
            self.SetLit()
        p = input("Continuing? =>(y/n)")
        if p == "n":
            print("end!!")
            #os._exit()
            sys.exit()
        elif p == "y":
            self.Call()

    def ShowMode(self):
        print("##############################")
        print("Which items are measured??")
        print("1. SinglePhe")
        print("2. MultiPhe")
        print("3. Pulse Width")
        print("4. HV-Gain Curve")
        print("5. Transit Time")
        print("6. Transit Time Spread")
        print("7. Afterpulse")
        print("8. Photocathod Dependency")
        print("c. Config")
        print('q. Exit')
        print("##############################")

        key = input("please enter the mode =>(1~9 or c or q)")
        if key == "q":
            print("End Process")
            #os._exit(os.EX_OK)
            sys.exit()
        else:
            return key
        
    def GetToday(self):
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        Y = now.strftime('%Y%m%d')
        y = now.strftime('%y%m%d')
        #print(d) 
        return Y, y

    def CreateDir(self, item = ''):
        Y, y = self.GetToday()
        dir_exsist = os.path.exists(self.Anapath+'/{0}/{1}/{2}'.format(y, self.pmt_serial, item))
        #print(self.Anapath+'/{0}/{1}/'.format(y, self.pmt_serial))
        if dir_exsist == True:
            print("Result Directory is Already Exsists!!")
            key = input("is it OK to continue?(y/n)")
            if key == "n":
                sys.exists()
        else:
            os.makedirs(self.Anapath+'/{0}/{1}/{2}'.format(y, self.pmt_serial, item))

        return self.Anapath+'/{0}/{1}/{2}'.format(y, self.pmt_serial, item)

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
        return dynode_num
    
    def SetHV(self):
        print("Setting HV...")
        self.hv = input("Please Check Power Supplyer and Enter HV-val ==> ")

    def SetLit(self):
        print("~~~~~ LIT setting ~~~~~~")
        print("Single_Lit : FW {0}".format(self.SingleLit))
        print("Multi_Lit : FW {0}".format(self.MultiLit))
        print("AfterPulse_Lit : FW {0}".format(self.APLit))
        print("~~~~~~~~~~~~~~~~~~~~~~~")


    def Set1PELight(self):

        #光量の調整
        flag = False
        while flag == False:
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

        #光量調整終了
        print("SinglePhe Lit => {0}".format(self.SingleLit))

    def SinglePheMeasurement(self):
        self.SetHV()
        singlepe_path = self.CreateDir(item = 'SinglePhe_{0}V/'.format(self.hv))
        file_name = self.date + '_' + self.pmt_serial + '_' + 'SinglePhe_{0}V'.format(self.hv) + ".root"

        ChangeFW(self.logfile, self.SingleLit)
        RunHageFusaScript(self.logfile, singlepe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
        ChangeFW(self.logfile, 36)
        RunHageFusaScript(self.logfile, singlepe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)

    def MultiPheMeasurement(self):
        self.SetHV()
        multipe_path = self.CreateDir(item = 'MultiPhe_{0}V/'.format(self.hv))
        file_name = self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(self.hv) + ".root"

        ChangeFW(self.logfile, self.MultiLit)
        RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
        ChangeFW(self.logfile, 36)
        RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)

    def HVGainMeasurement(self):
        multipe_path = self.CreateDir(item = 'HVGainCurve/')
        for hv in range(1400, 800, -100):
            input('{0}V Measurement Start! Please Check Power Supplyer! Continue?=>(y/n) '.format(hv))
            file_name = self.date + '_' + self.pmt_serial + '_' + 'MultiPhe_{0}V'.format(hv) + ".root"
            ChangeFW(self.logfile, self.MultiLit)
            RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_s, self.event_s, serial = self.drs4board)
            ChangeFW(self.logfile, 36)
            RunHageFusaScript(self.logfile, multipe_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board)

            print('{0}V Measurement Done!'.format(hv))
        print("End HV-Gain Measurement")

    def AfterPulseMeasurement(self):
        afterpulse_path = self.CreateDir(item = 'Afterpulse/')
        input('AfterPulse Measurement Start! Please connect signal line to Function Generator! Continue?=>(y/n) ')

        timing = [0.0, 0.95e-6, 1.85e-6, 2.75e-6, 3.65e-5]
        for i in range(5):
            ChangeDelay(timing[i])
            file_name = self.date + '_' + self.pmt_serial + '_' + 'Afterpulse_{0}-{1}us'.format(i, i+1) + ".root"
            ChangeFW(self.logfile, self.APLit)
            RunHageFusaScript(self.logfile, afterpulse_path+file_name, self.Treename_s, self.evnet_a, serial = self.drs4board, delay = 850.0, freq= 1.0)
            ChangeFW(self.logfile, 36)
            RunHageFusaScript(self.logfile, afterpulse_path+file_name, self.Treename_d, self.event_d, serial = self.drs4board, delay = 850.0, freq= 1.0)

        
    
if __name__ == "__main__":
    hoge = PMT_Merin_sys()