import sys
from utils import * 
from config_utils import * 
from test_utils import *

def main(argv="unknown.py"):

	WriteREG("GTX.RESET_CTRL", (1<<28) | (1<<24) | 0xF)
	WriteREG("GTX.CTRL", 0x2)

	hit_size = 2**14
	pattin_size = 2**10
	instr_size = 2**10
	spy_size = 2**15

	hits = []
	for i in xrange(8):
		data = [j+1|(i<<24) for j in xrange(hit_size)]
		hits.append(data)
		Upload("GTX.HIT%d"%(i), data)
	pattins = []
	for i in xrange(2):
		data = [j+1|((i+8)<<24) for j in xrange(pattin_size)]
		pattins.append(data)
		Upload("GTX.PATTIN%d"%(i), data)

	instr = []

	instr.append(iDATA) # 0
	instr.append(iIDLE) # 1
	instr.append(iDATA | 10) # 2
	instr.append(iOPCODE | opcode_init | iHOLD_PATTOUT_FLAG) # 3
	instr.append(iDATA) # 4
	instr.append(iGOTO | 4) # 5
	instr.append(iADDR | 2) # 6
	instr.append(iDATA) # 7
	instr.append(iIDLE | 5) # 8
	instr.append(iDATA | 1) # 9
	instr.append(iGOTO | iINFINITE) # 10
	instr.append(iADDR | len(instr)-1) # 11
	
	Upload("GTX.HIT_INSTR", instr)
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)

	Upload("SPY.SPY", [0]*spy_size)
	Upload("SPY.SPY_EXTRA", [0]*spy_size)
	WriteREG("SPY.HOLD_ADDR", spy_size-5)
	WriteREG("SPY.CTRL", 0x7 | (0<<4))

	WriteREG("GTX.CTRL", 0x1 | (1<<9))

	spy = Dump("SPY.SPY")
	spy_extra = Dump("SPY.SPY_EXTRA")
	for i in xrange(len(spy)):
		print "i %7d spy: %8x spy_extra: %8x hold: %d data_addr: %4x instr_addr: %3x charisk: %1x"%(i,
			spy[i], spy_extra[i], (spy_extra[i] >> 31) & 0x1, (spy_extra[i] >> 16) & 0x7FFF, (spy_extra[i] >> 4) & 0xFFF, spy_extra[i] & 0xF)

if __name__ == '__main__':
	main(sys.argv)
 
