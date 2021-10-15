import os
import subprocess
import psutil
import time


#get as variables: path_to_file, interval time
path_to_file = input("Path to file:")
interval_time = input("interval time")

pid = subprocess.Popen(path_to_file)

def stat_for_unix():
    while True:
        #get CPU
        cpu_usage =
        proc_path = f'/proc/{pid}/status'
        #get Resident Set Size
        rs_size = os.system("cat " + proc_path + " | grep VmRSS | awk '{print $2}'") #збс pid захардкодила
        #get Virtual Memory Size /proc/[pid]/status | grep 'VMSize'
        vm_size = os.system("cat " + proc_path + " | grep VmSize | awk '{print $2}'")
        #get open file descriptors count /proc/[pid]/status | grep 'FDSize'
        fd_count = os.system(f"ls -1 {proc_path} | ws")

        result = {'cpu_usage': cpu_usage, 'rs_size': rs_size, "vm_size": vm_size, "fd_count": fd_count}
        json = json.dump(result)

        #suspend to json file or to SQLite

        time.sleep(interval_time)

def stat_for_mac:
    print('This OS type is not supported yet')


def stat_for_windows:
    print('This OS type is not supported yet')
    #while True:
        #get CPU
        #get Resident Set Size
        #get Virtual Memory Size
        #get open file descriptors count
        #suspend to json file or to SQLite

os_type = os.uname()
if "Linux" in os_type:
    stat_for_unix()
elif "Mac" in os_type:
    stat_for_mac()
elif "Windows" in os_type:
    stat_for_windows()
else:
    print("This OS type is not supported yet")