import sys
from utils import * 
from test_utils import * 

def main(argv=["unknown.py"]):
	if len(argv) > 1:
		if argv[1] == "-h":
			print "[dumpname]"
			sys.exit()

	res = ReadErrorRate(silent = False)

	if len(argv) > 1:
		debug = False
		CTRL = ReadREG("PATTOUT.CTRL", debug)
		WriteREG("PATTOUT.CTRL", CTRL | 0x1, debug, title="Freeze")
		predicted_ram = Dump("PATTOUT.PREDICTED_PATTERNS")
		pattout_ram = Dump("PATTOUT.PATTOUT")
		expected_ram = Dump("PATTOUT.EXPECTED")
		received_ram = Dump("PATTOUT.RECEIVED")
		extra_ram = Dump("PATTOUT.EXTRA")
		WriteREG("PATTOUT.CTRL", CTRL & 0xFE, debug, title="UnFreeze")

		f = open(argv[1], 'w')
		f.write(res[3]+"\n")
		f.write("i predicted: x pattout: x expected: x received: x extra: x\n")

		for i in xrange(len(pattout_ram)):
			f.write("%d predicted: %8x pattout: %8x expected: %8x received: %8x event: %8x extra: %8x\n"%(i,
				predicted_ram[i], pattout_ram[i], expected_ram[i]&0xFF00FFFF, received_ram[i]&0xFF00FFFF, ((expected_ram[i]&0x00FF0000)>>16) | ((received_ram[i]&0x00FF0000)>>8), extra_ram[i]))

	return {"err_rate" : res, "predicted" : predicted_ram, "expected" : expected_ram, "received" : received_ram }

if __name__ == '__main__':
	main(sys.argv)
