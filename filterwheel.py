import subprocess
import time
from generalfunc import *

#Filterwheelの操作をする
def ChangeFW(logfile, fw_num):

    with open(logfile, "a") as fp:
        subprocess.call(['multifw-control.sh', '{0}'.format(fw_num)], stdout=fp, stderr=fp)
    print(Color.BLUE + "FW move to => {0}".format(fw_num) + Color.RESET)
    time.sleep(3)
    