# proc_stat_py
statan - utility to analyze process statistic: process cpu(%), resident set size, virtual memory size, 
    count of file descriptors. For linux - getting this info by parsing procfs. This utility will start the process 
    by path to process file and end it when you press "Ctrl + C" to end statan \n usage:  statan.py -p <Path to 
    process file> -i <interval time, sec> -l <path to log file (statan will create if not exist> or: \n statan.py 
    --process <Path to process file> --interval <interval time, sec> --logfile <path to log file>. -h or --help print 
    this help
