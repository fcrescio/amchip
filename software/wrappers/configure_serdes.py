import sys
from config_utils import *

def main(argv=["unknown.py"]):
	if len(argv) > 1:
		if argv[1] == "-h":
			print "[mult div (default 20 1) [mode (default 0 means Normal)]]"
			sys.exit()
	mult = 20
	div = 1
	if len(argv) > 2:
		mult = int(argv[1])
		div = int(argv[2])

	mode = MODE_Normal
	if len(argv) > 3:
		mode = int(argv[3])

	ConfigureSerDes(mult, div, mode)

if __name__ == '__main__':
	main(sys.argv)
