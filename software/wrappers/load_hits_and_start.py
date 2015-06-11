import sys
from utils import * 
from test_utils import *

def main(argv="unknown.py"):
	if len(argv) < 4:
		print "dataname eventSize threshold"
		sys.exit()

	data = UnPickle(argv[1])
	LoadHitsAndStart(data, eventSize=int(argv[2]), threshold=int(argv[3]))

if __name__ == '__main__':
	main(sys.argv)
