import sys
from utils import * 
from test_utils import * 

def main(argv="unknown.py"):
	if len(argv) < 6:
		print "bankname offset dataname eventsize thr [streamname [eventname]]"
		sys.exit()

	bank = UnPickle(argv[1])
	data = UnPickle(argv[3])

	stream = PredictStream(bank, offset=int(argv[2]), data=data, eventSize=int(argv[4]), threshold=int(argv[5]))
	expectlist = stream[0]
	eventlist = stream[1]

	if len(argv) > 6:
		Pickle(argv[6], expectlist)

	if len(argv) > 7:
		Pickle(argv[7], eventlist)

if __name__ == '__main__':
	main(sys.argv)
