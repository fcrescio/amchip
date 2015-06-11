import sys
from config_utils import * 

def main(argv="unknown.py"):
	if len(argv) < 2:
		print "clock (a - for AMchip clock, g - for GTX clock) [frequency (default 100 MHz)]"
		sys.exit()
	freq = 100
	if len(argv) > 2:
		freq = float(argv[2])
	SetFrequencyMHz(argv[1], freq)

if __name__ == '__main__':
	main(sys.argv)
