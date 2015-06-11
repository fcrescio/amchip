import sys
from utils import * 
from config_utils import * 
from test_utils import *
import read_error_rate, set_volt, read_power_consumption

def main(argv="unknown.py"):
    t = Tick()
    print("Configure the FPGA clock and GTX at nominal frequency of 100 MHz / 2 gbps")
    freqMHz = 100.0
    voltV = 1.0
    silent = False

    read_power_consumption.main(["", voltV])
    link_speedGbps = 2.0
    succeeded = False
    while not succeeded:
        try:
            conf = SetFreqMHzAndConfigSerDesGbps(freqMHz, link_speedGbps)
            succeeded = True
        except SpeedException as e:
            link_speedGbps = link_speedGbps * 0.95

    StopGTX()
    locked = False
    j = GetJTAG()
    s = SERDES(j)
    while not locked:
        j.NewSession()
        toChipErr_info = s.SEL_STAT(pattin0_pattout | SysStatReg)
        j.Dispatch()
        ToChipErr = j.Retrieve(toChipErr_info) & (1<<28)
        locked = ToChipErr == 0
        print "locked", locked
    print("Configure the AMchip")
    THRESHOLD=8
    PATTERNS=2048
    EVLEN=512
    OFFSET=0
    INJEVT=5000

    bank = GenBank(PATTERNS)
    with open("last_run.bank","w") as f:
        for addr, pattern in enumerate(bank):
            f.write("%x : %s\n"%(addr,["%x"%(word) for word in pattern]))
    LoadBank(bank, OFFSET)

    data = GenDataFromBank(16384, bank, INJEVT)
    with open("last_run.events","w") as f:
        for event in range(16384/EVLEN):
            f.write("event: %d\n"%(event))
            for word in range(EVLEN):
                f.write("%s\n"%(["%x"%(busw) for busw in data[word+EVLEN*event]]))
            f.write("+++\n")
    stream = PredictStream(bank, OFFSET, data, EVLEN, THRESHOLD)
                # somelist = stream[0] # unused
    expectedEvents = stream[1]
    with open("last_run.roads","w") as f:
        for idx, event in enumerate(expectedEvents):
            f.write("event: %d\n"%(idx))
            for word in event:
                f.write("%x\n"%(word))
            f.write("---\n")
    WriteFullRateProgram(expectedEvents, EVLEN)
    LoadHits(data)
    LoadPredictedPatterns(EventsToList(expectedEvents))
    
    with open("last_run.shmoo", "w") as fshmoo:
        for freq in xrange(100,161,20):
            for voltage in xrange(800,1301,100):
                fshmoo.write("%f - %d - "%(voltage/1000.0,freq))
                read_power_consumption.main(["", voltage/1000.0])
                succeeded = False
                link_speedGbps = freq*20/1000.0
                while not succeeded:
                    try:
                        conf = SetFreqMHzAndConfigSerDesGbps(freq, link_speedGbps)
                        succeeded = True
                    except SpeedException as e:
                        link_speedGbps = link_speedGbps * 0.95

                StopGTX()
                locked = False
                j = GetJTAG()
                s = SERDES(j)
                while not locked:
                    j.NewSession()
                    toChipErr_info = s.SEL_STAT(pattin0_pattout | SysStatReg)
                    j.Dispatch()
                    ToChipErr = j.Retrieve(toChipErr_info) & (1<<28)
                    locked = ToChipErr == 0
                print "locked", locked
                print("Reset AMchip and reconfigure")                
                StartGTX(THRESHOLD)
                res = ReadErrorRate(silent = True)
                if res[2]>0:
                    print("No good %d, retry"%(res[2]))
                    StopGTX()
                    StartGTX(THRESHOLD)
                    res = ReadErrorRate(silent = True)
                if res[2]>0:
                    dumpedEvents = DumpPattoutEvents()
                    pattout_results = CompareEvents(dumpedEvents, expectedEvents, False)
                    print("No good: %d, go on"%(res[2]))
                    fshmoo.write("%d\n"%(res[2]))
                    continue
                sleep(10)
                res = ReadErrorRate(silent = True)
                if (res[2] == 0):
                    print("Verify")
                    dumpedEvents = DumpPattoutEvents()
                    totlen = 0
                    for event in dumpedEvents:
                        totlen += len(event)
                    if totlen == 0:
                        print("All empty events!\n")
                        fshmoo.write("nil\n")
                    else:
                        pattout_results = CompareEvents(dumpedEvents, expectedEvents, True)
                    print(pattout_results)
                fshmoo.write("%d\n"%(res[2]))

if __name__ == '__main__':
	main(sys.argv)
