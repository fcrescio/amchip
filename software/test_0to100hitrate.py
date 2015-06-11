import sys
from utils import * 
from config_utils import * 
from test_utils import *
import read_error_rate, set_volt, read_power_consumption

def main(argv="unknown.py"):
	if len(argv) > 1:
		if argv[1] == "-h":
			print " [resultname, freqMHz, voltmV]"
			sys.exit()

	freqMHz = 100.0
	if len(argv) > 2:
		freqMHz = float(argv[2])
	voltV = 1.0
	if len(argv) > 3:
		voltV = float(argv[3])/1000.0

	silent = False
	if len(argv) > 4:
		silent = True

	THRESHOLD = 0
	print "Test with random bank and threshold", THRESHOLD
	t = Tick()

	print "Configuring Clocks and GTXs"

	read_power_consumption.main(["", voltV])
	link_speedGbps = 2.0
	print freqMHz
	if freqMHz<99.999999:
		link_speedGbps = 0.95 * link_speedGbps * freqMHz / 100.0

	succeeded = False
	while not succeeded:
		try:
			conf = SetFreqMHzAndConfigSerDesGbps(freqMHz, link_speedGbps)
			succeeded = True
		except SpeedException as e:
			link_speedGbps = link_speedGbps * 0.95

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

	PATTERNS=2048
	EVLEN=4096
	OFFSET=0

	StopGTX()

	bank = GenBank(PATTERNS)
	LoadBank(bank, OFFSET)

	INJEVT=EVLEN/2

	data = GenData(16384, bank, INJEVT)

	stream = PredictStream(bank, OFFSET, data, EVLEN, THRESHOLD)
	# somelist = stream[0] # unused
	expectedEvents = stream[1]

	LoadHits(data)
	LoadPredictedPatterns(EventsToList(expectedEvents))

	WriteHitSendProgram(0)
	StartGTX(THRESHOLD)
	sleep(0.1)
	read_power_consumption.main(["", voltV])
        WriteHitSendProgram(100)
        StartGTX(THRESHOLD)
        sleep(0.1)
	read_power_consumption.main(["", voltV])


	suffix = "_%.3f_MHz_%.5f_V.res"%(freqMHz, voltV)
	if len(argv) > 1:
		Pickle(argv[1]+suffix, all_results)

	Tock(t, "Execution of the test")

if __name__ == '__main__':
	main(sys.argv)
