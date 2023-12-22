import subprocess
import time

#Filterwheelの操作をする
def ChangeFW(logfile, fw_num):

    with open(logfile, "a") as fp:
        subprocess.call(['multifw-control.sh', '{0}'.format(fw_num)], stdout=fp, stderr=fp)
    print("FW move to => {0}".format(fw_num))
    time.sleep(3)
    