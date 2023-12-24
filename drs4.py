import subprocess
import sys
import time
from tqdm import tqdm
import threading


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

#DRS4の操作
def RunHageFusaScript2(logfile, file, tree, eventnum, serial=2386, delay = 0.0, freq=5.0):
    READDrs4_path = '/Users/cta/Software/JustReadDrs4_Sunada_20210408/ReadDrs4'
    try:
        print("Run ReadDrs4!")
        #print(READDrs4_path, "-s", "{0}".format(serial), "-i", "0", '-f', "{0}".format(freq), "-d", "{0}".format(delay), "-e", "{0}".format(eventnum), "-m", "{0}".format(tree), "-n", "0", "-0", "{0}".format(file))
        with open(logfile, "a") as fp:
            subprocess.call([READDrs4_path, "-s", "{0}".format(serial), "-i", "0", '-f', "{0}".format(freq), "-d", "{0}".format(delay), "-e", "{0}".format(eventnum), "-m", "{0}".format(tree), "-n", "0", "-0", "{0}".format(file)], stdout=fp)
    except:
        print("ERROR with DRS4!")

def RunHageFusaScript(logfile, file, tree, eventnum, serial=2386, delay = 0.0, freq=5.0):
    READDrs4_path = '/Users/cta/Software/JustReadDrs4_Sunada_20210408/ReadDrs4'

    def RunScript():
        try:
            print("Run ReadDrs4!")
            #print(READDrs4_path, "-s", "{0}".format(serial), "-i", "0", '-f', "{0}".format(freq), "-d", "{0}".format(delay), "-e", "{0}".format(eventnum), "-m", "{0}".format(tree), "-n", "0", "-0", "{0}".format(file))
            with open(logfile, "a") as fp:
                subprocess.call([READDrs4_path, "-s", "{0}".format(serial), "-i", "0", '-f', "{0}".format(freq), "-d", "{0}".format(delay), "-e", "{0}".format(eventnum), "-m", "{0}".format(tree), "-n", "0", "-0", "{0}".format(file)], stdout=fp)
        except:
            print("ERROR with DRS4!")

    def Progressbar():
        time.sleep(1.5)
        for i in tqdm(range(eventnum)):
            time.sleep(0.00225)

    thread1 = threading.Thread(target = RunScript)
    thread2 = threading.Thread(target = Progressbar)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    command = ["tail", "-n", "3", logfile, "|", "tac", "|", "head", "-n", "1"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_stdout = proc.stdout.read() # 標準出力の場合
    output_stderr = proc.stderr.read() # 標準エラー出力の場合
    #print(output_stdout)
    if "DAQ end" in output_stdout.decode():
        print(Color.GREEN + "END DAQ!" + Color.RESET)
    else:
        print(Color.RED + "DAQ is not end correctly...." + Color.RESET)

def Oscillo(serial=2386, delay = 0.0, freq = 5.0):
    READDrs4_path = '/Users/cta/Software/JustReadDrs4_Sunada_20210408/ReadDrs4'
    try:
        subprocess.call([READDrs4_path, "-s", "{0}".format(serial), "-i", "0", '-f', "{0}".format(freq), "-d", "{0}".format(delay), "-e", "1000", "-m", "temp", "-n", "0", "-0", "Checking_hagefusa_script.root", "-o"])
    except KeyboardInterrupt:
        sys.exit()

def CalDrs4():
    READDrs4_path = '/Users/cta/Software/JustReadDrs4_Sunada_20210408/ReadDrs4'
    try:
        subprocess.call([READDrs4_path, '-c', 'time', '-f', '5.0'])
    except:
        print("DRS4 Callibration Error!")
    
    try:
        subprocess.call([READDrs4_path, '-c', 'volt', '-f', '5.0'])
    except:
        print("DRS4 Callibration Error!")

    print("Callibration Done!")