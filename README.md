# proc_stat_py
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
