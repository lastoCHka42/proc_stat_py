#!/usr/bin/env python3
import os
import subprocess
import time
import json
import sys
import signal
import getopt


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


def stat_for_unix(pid, path_to_log_file, interval_time):
    # get CPU
    p = subprocess.Popen(['./top.sh', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    cpu_usage = float(out.decode("utf-8"))

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

    with open(path_to_log_file, 'a') as f:
        result = {'cpu_usage': cpu_usage, 'rs_size': rs_size, "vm_size": vm_size, "fd_count": fd_count,
                  'time': time.ctime()}
        json.dump(result, f)
        f.write('\n')

    # suspend to json file
    with open(path_to_log_file, 'a+') as f:
        res = {time.ctime(): {'cpu_usage': cpu_usage, 'rs_size': rs_size, "vm_size": vm_size, "fd_count": fd_count}}
        json.dump(res, f)


def stat_for_windows():
    print('This OS type is not supported yet')
    # while True:
    # get CPU
    # get Resident Set Size
    # get Virtual Memory Size
    # get open file descriptors count
    # suspend to json file or to SQLite


def main():
    #set defaul vars
    path_to_file = 'default'
    interval_time = 10
    path_to_log_file = 'log.json'

    # get variables as arguments:
    usage = '''statan - utility to analyze process statistic: process cpu(%), resident set size, virtual memory size, 
    count of file descriptors. For linux - getting this info by parsing procfs. This utility will start the process 
    by path to process file and end it when you press "Ctrl + C" to end statan \n usage:  statan.py -p <Path to 
    process file> -i <interval time, sec> -l <path to log file (statan will create if not exist> or: \n statan.py 
    --process <Path to process file> --interval <interval time, sec> --logfile <path to log file>. -h or --help print 
    this help '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hp:i:l:', ['help', 'process=', 'interval=', 'logfile='])

    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    if len(opts) == 0 or len(opts) > 3:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(usage)
            sys.exit(2)
        elif opt in ('-p', '--process'):
            path_to_file = arg
        elif opt in ('-i', '--interval'):
            interval_time = arg
        elif opt in ('-l', '--logfile'):
            path_to_log_file = arg
    if path_to_file == 'default':
        print('No path to process file given')
        sys.exit(2)

    pid = subprocess.Popen(path_to_file).pid

    # exit with ctrl + c
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        os.system(f'kill -9 {pid}')
        sys.exit(0)

    os_type = os.uname()
    if "Linux" in os_type:
        signal.signal(signal.SIGINT, signal_handler)
        while True:
            stat_for_unix(pid, path_to_log_file, interval_time)
            time.sleep(int(interval_time))

    # elif "Windows" in os_type:
    #while True:
    #     stat_for_windows()
    #     time.sleep(int(interval_time))
    else:
        print("This OS type is not supported yet")


if __name__ == '__main__':
    main()
