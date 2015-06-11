import sys
from config_utils import * 

def main(argv=["unknown.py"]):
	if len(argv) > 1:
		if argv[1] == "-h":
			print "[runTime sec (default -1 means forever) [silent (default 0 means False)]]"
			sys.exit()
	runTime = -1 # forever
	if len(argv) > 1:
		runTime = float(argv[1])
	silent = False
	if len(argv) > 2:
		silent = int(argv[2]) != 0
	return ReadPRBSErr(runTime, silent)

if __name__ == '__main__':
	main(sys.argv)
