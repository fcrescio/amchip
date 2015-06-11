import sys
from utils import * 
from config_utils import * 
from test_utils import *

def main(argv="unknown.py"):

	WriteREG("SPY.CTRL",0x70)
	spy = Dump("SPY.SPY")
	spy_extra = Dump("SPY.SPY_EXTRA")
	for i in xrange(len(spy)):
		print "i %7d spy: %8x spy_extra: %8x hold: %d data_addr: %4x instr_addr: %3x charisk: %1x"%(i,
			spy[i], spy_extra[i], (spy_extra[i] >> 31) & 0x1, (spy_extra[i] >> 16) & 0x7FFF, (spy_extra[i] >> 4) & 0xFFF, spy_extra[i] & 0xF)

if __name__ == '__main__':
	main(sys.argv)
 
