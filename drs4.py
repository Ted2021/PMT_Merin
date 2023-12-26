import subprocess
import sys
import time
from tqdm import tqdm
import threading
from generalfunc import *

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
    thread2.join(0)     #ReadDRS4がおわったら強制的に落ちる

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