import sys
from utils import *
from test_utils import *

def main(argv="unknown.py"):
	if len(argv) < 2:
		print "bankname [offset]"
		sys.exit()

	bank = UnPickle(sys.argv[1])

	offset = 0
	if len(argv) > 2:
		offset = int(sys.argv[2])

	LoadBank(bank, offset)

if __name__ == '__main__':
	main(sys.argv)

