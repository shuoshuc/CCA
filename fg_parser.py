#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv  
import re
import os.path
from pathlib import Path
from numpy import square, sum

def logParser(logname):
    entries = []
    csvfile = logname.split('.')[0] + '.csv'
    with open(logname, 'r') as f:
        for line in f:
            fid = -1
            chunks = line.split()
            if len(chunks) == 0:
                continue
            elif chunks[0] == 'S':
                fid = int(chunks[1])
                chunks.pop(0)
                chunks.pop(0)
            elif 'S' in chunks[0]:
                fid = int(chunks[0][1:])
                chunks.pop(0)
            else:
                continue
            ts, thru, cwnd, rtt = chunks[1], chunks[2], chunks[10], chunks[20]
            entries.append((fid, ts, thru, cwnd, rtt))
    with open(csvfile, 'w', encoding='UTF8') as outf:
        writer = csv.writer(outf)
        writer.writerow(['flow', 'time', 'thru(Mbps)', 'cwnd', 'rtt(msec)'])
        writer.writerows(entries)

def avgJFI(folder):
    tputs = []
    jfi = []
    pattern = re.compile(r".*D:.*through = \d+\.\d+/(\d+\.\d+) \[Mbit/s\].*")
    logs = Path(folder).glob('*.log')
    for log in logs:
        with open(log, 'r') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    tputs.append(float(match.group(1)))
        jfi.append([square(sum(tputs)) / (len(tputs) * sum(square(tputs)))])
    with open(os.path.join(folder, 'jfi.csv'), 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['JFI'])
        writer.writerows(jfi)

def waitThru(folder):
    wait_tputs = []
    pattern = re.compile(r".*D:.*read delay = (\d+\.\d+).*through = "
                         r"\d+\.\d+/(\d+\.\d+) \[Mbit/s\].*")
    logname_pattern = re.compile(r".*run(\d+)\.log")
    logs = Path(folder).glob('*.log')
    for log in logs:
        log_match = logname_pattern.match(str(log))
        if log_match:
            run = log_match.group(1)
        with open(log, 'r') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    wait_tputs.append((run, float(match.group(1)),
                                       float(match.group(2))))
    with open(os.path.join(folder, 'wait_tput.csv'), 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['run', 'wait(sec)', 'thru(Mbps)'])
        writer.writerows(wait_tputs)

if __name__ == "__main__":
    if sys.argv[1] == 'log':
        logParser(sys.argv[2])
    elif sys.argv[1] == 'jfi':
        avgJFI(sys.argv[2])
    elif sys.argv[1] == 'wait':
        waitThru(sys.argv[2])
