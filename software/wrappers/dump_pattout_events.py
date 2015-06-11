import sys
from utils import * 
from test_utils import *

def main(argv="unknown.py"):
	if len(argv) < 2:
		print "buflen [streamname]"
		sys.exit()

	#events = DumpPattoutEvents(buflen=int(argv[1]))
	events = DumpPattoutEvents()
	if len(argv) > 2:
		Pickle(argv[2], events)

if __name__ == '__main__':
	main(sys.argv)
