import sys
from utils import * 
from test_utils import * 

def main(argv="unknown.py"):
	if len(argv) < 4:
		print "datasize bankname injectFactor [dataname]"
		sys.exit()

	bank = UnPickle(argv[2])
	data = GenData(size=int(argv[1]), bank=bank, injectFactor=int(argv[3]))

	if len(argv) > 4:
		Pickle(argv[4], data)

if __name__ == '__main__':
	main(sys.argv)
