import sys
from utils import * 
from test_utils import *

def main(argv="unknown.py"):
	if len(argv) < 3:
		print "pattout expect [result]"
		sys.exit()

	eventlist = UnPickle(argv[1])
	expectlist = UnPickle(argv[2])

	result = CompareEvents(eventlist, expectlist)

	if len(argv) > 3:
		Pickle(argv[3], result)

if __name__ == '__main__':
	main(sys.argv)
