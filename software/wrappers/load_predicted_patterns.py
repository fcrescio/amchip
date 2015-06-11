import sys
from utils import * 
from test_utils import *

def main(argv="unknown.py"):
	if len(argv) < 3:
		print "patternsname ramSize"
		sys.exit()

	ramSize = int(argv[2])
	patterns = EventsToList(UnPickle(argv[1]))
	# patterns[8] = 0

	LoadPredictedPatterns(patterns, ramSize)

if __name__ == '__main__':
	main(sys.argv)
