import sys
from utils import *
from config_utils import *

def main(argv=["unknown.py"]):
	scan_freq = True
	if len(argv) > 1:
		if argv[1][0] == "f":
			scan_freq = True
		elif argv[1][0] == "s":
			scan_freq = False
		else:
			print Error_("Please specify correctly what to scan: f - frequency, s - speed")
			raise
	print Header_("Frequency scan") if scan_freq else Header_("Speed scan")

	frequencies = [10*i for i in xrange(3,21)]
	frequencies.extend([200+20*i for i in xrange(1,6)])
	speeds = [0.1*i for i in xrange(5, 41)]
	if scan_freq:
		speeds = [2.0]
	else:
		frequencies = [100.0]

	executionTimeSec = 2.5
	if len(argv) > 2:
		executionTimeSec = float(argv[2])
	if executionTimeSec < 2:
		print Error_("Need to run test at least for 2 seconds to get proper results")
		raise

	if len(argv) > 3:
		userValues = []
		for x in xrange(3, len(argv)):
			userValues.append(float(argv[x]))
		if scan_freq:
			frequencies = userValues
		else:
			speeds = userValues

	print Header_("Frequencies "+str(frequencies))
	print Header_("Speeds "+str(speeds))

	for freq in frequencies:
		for speed in speeds:
			try:
				param = SetFreqMHzAndConfigSerDesGbps(freq, speed, MODE_PRBS7)

				err = ReadPRBSErr(executionTimeSec, silent=1)
				toC = Ok_ if err["ToChip"] == 0 else Error_
				fromC = Ok_ if err["FromChip"] == 0 else Error_

				print "Link %.5f Gbit/s = %.5f MHz * %d / %d."%(param["real_speed"], param["real_freq"], param["sMult"], param["sDiv"])
				print "Error rate at "+Warning_("%.2f MHz"%(param["real_freq"]))+" is "+toC("%.2g [errs/sec] to chip"%(err["ToChip"]/(executionTimeSec-1.5)))+" and "+fromC("%.2g [errs/sec] from chip"%(err["FromChip"]/(executionTimeSec-1.5)))+"."
			except SpeedException as e:
				print "Skipping speed %.5f Gbit/s."%(speed)
			print "################################################################################\n"

if __name__ == '__main__':
	main(sys.argv)
