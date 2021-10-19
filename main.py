import os
import subprocess
import time
import json

# get as variables: path_to_file, interval time
path_to_file = input("Path to process file")
interval_time = input("interval time, sec")
path_to_log_file = input("path to log file")

pid = subprocess.Popen(path_to_file).pid


def to_bytes(integer, units):
    if 'k' in units:
        integer *= 1024
    elif ('m' or 'M') in units:
        integer *= 10 ** 20
    elif ('g' or 'G') in units:
        integer *= 10 ** 30
    elif ('t' or 'T') in units:
        integer *= 10 ** 40
    return integer


def stat_for_unix():
    while True:
        # get CPU
        p = subprocess.Popen(['./top.sh', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        cpu_usage = int(out.decode("utf-8"))

        proc_path = f'/proc/{pid}/status'

        # get Resident Set Size VmRSS, Virtual Memory Size
        with open(proc_path, 'r') as f:
            for lines in f:
                if 'VmRSS' in lines:
                    space_to_units = lines.rfind(' ', 0)  # last space to parse units
                    rs_units = lines[space_to_units + 1:-1].strip()  # parse units without spaces
                    start = lines.find(' ')  # first space to parse value
                    rs_size = int(lines[start:space_to_units].strip())  # parse value without spaces, change to integer
                    rs_size = to_bytes(rs_size, rs_units)  # change kb (or Mb, or Gb...) to bytes for real statistic
                if 'VmSize' in lines:  # the same with rss
                    space_to_units = lines.rfind(' ', 0)
                    vm_units = lines[space_to_units + 1:-1].strip()
                    start = lines.find(' ')
                    vm_size = int(lines[start:space_to_units].strip())
                    vm_size = to_bytes(vm_size, vm_units)

        # get fd count
        counter = [i for i in os.listdir(f'/proc/{pid}/fd')]
        fd_count = len(counter)
        print(fd_count)

        with open(path_to_log_file, 'a') as f:
            result = {'cpu_usage': cpu_usage, 'rs_size': rs_size, "vm_size": vm_size, "fd_count": fd_count,
                      'time': time.ctime()}
            json.dump(result, f)
            f.write('\n')

        # suspend to json file
        with open(path_to_log_file, 'a') as f:
            res = {time.ctime(): {'cpu_usage': cpu_usage, 'rs_size': rs_size, "vm_size": vm_size, "fd_count": fd_count}}
            json.dump(res, f)

        time.sleep(int(interval_time))
        
        
#exit with ctrl + c
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def stat_for_windows():
    print('This OS type is not supported yet')
    # while True:
    # get CPU
    # get Resident Set Size
    # get Virtual Memory Size
    # get open file descriptors count
    # suspend to json file or to SQLite


os_type = os.uname()
if "Linux" in os_type:
    stat_for_unix()
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    os.system(f'kill -9 {pid}')
# elif "Mac" in os_type:
#     stat_for_mac()
# elif "Windows" in os_type:
#     stat_for_windows()
else:
    print("This OS type is not supported yet")
