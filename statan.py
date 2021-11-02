#!/usr/bin/env python3
import os
import subprocess
import time
import json
import sys
import signal
import getopt


def to_bytes(integer: int, units: str) -> int:
    ''' gets memory size as integer (value) and units as string (e.g.: 
    integer = 128, units = kb). Returns memory size in bytes as integer.
    '''
    if 'k' in units:
        integer *= 1024
    elif ('m' or 'M') in units:
        integer *= 10 ** 20
    elif ('g' or 'G') in units:
        integer *= 10 ** 30
    elif ('t' or 'T') in units:
        integer *= 10 ** 40
    return integer


def stat_for_unix(pid: int, path_to_log_file: str):
    ''' gets info about process: CPU usage(%), Resident Set Size, 
    Virtual Memory Size, count of File Descriptors.
    Takes pid as argument to get access to correct procfs file
    uses top.sh script to get cpu usage
    takes path to log file as argument. If file don't exist, create it.
    get CPU using top.sh script'''

    p = subprocess.Popen(['./top.sh', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    cpu_usage = float(out.decode("utf-8"))

    # get Resident Set Size, Virtual Memory Size from procfs, find the path by pid (taken as argument to function)

    proc_path = f'/proc/{pid}/status'

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

    # get fd count - looking how many items in fd directory (from procfs)
    counter = [i for i in os.listdir(f'/proc/{pid}/fd')]
    fd_count = len(counter)

    # write info to logfile as a json. Create if file don't exist
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
    # set defaul vars
    path_to_file = 'default'
    interval_time = 10
    path_to_log_file = 'log.json'

    usage = '''
    NAME: 
        statan.py - utility to analyze process statistic: process cpu(%), resident set size, virtual memory size, 
    count of file descriptors. For linux - getting this info by parsing procfs. This utility will start the process 
    by path to process file and end it when you press "Ctrl + C" to end statan 
    USAGE:  
        statan.py [options...]
    OPTIONS:
        -p, --process <Path to process file> - set path to process file. If not given, utility returns error message
        -i, --interval <interval time, sec> - set interval to measure parameters in seconds. Default - 10 sec
        -l, --logfile <path to log file> - set path to log file. Statan will create file if not exist. Default log.json
        -h, --help - print this help
         '''

    # get variables as arguments from CLI or sys exit if not given:

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

    # check os type to use correct function

    os_type = os.uname()
    if "Linux" in os_type:
        signal.signal(signal.SIGINT, signal_handler)
        while True:
            stat_for_unix(pid, path_to_log_file)
            time.sleep(int(interval_time))

    elif "Windows" in os_type:
        stat_for_windows()
    #     time.sleep(int(interval_time))
    else:
        print("This OS type is not supported yet")


if __name__ == '__main__':
    main()
