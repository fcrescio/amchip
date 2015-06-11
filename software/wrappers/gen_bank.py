import sys
from utils import * 
from test_utils import * 

def main(argv="unknown.py"):
	if len(argv) < 2:
		print "banksize [bankname]"
		sys.exit()

	bank = GenBank(size=int(argv[1]))

	if len(argv) > 2:
		Pickle(argv[2], bank)

	return bank

if __name__ == '__main__':
	main(sys.argv)
