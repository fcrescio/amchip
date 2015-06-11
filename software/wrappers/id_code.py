import sys
from utils import * 
from test_utils import * 

def main(argv=["unknown.py"]):
	id_code = ReadIDCODE()
	if id_code == 0x50004071:
		highlight_ = Ok_
	else:
		highlight_ = Error_
	print highlight_("\tIDCODE = "+hex(id_code))
	return id_code

if __name__ == '__main__':
	main(sys.argv)
	
	from pylab import *

	t = arange(0.0, 2.0, 0.01)
	s = sin(2*pi*t)
	plot(t, s)

	xlabel('time (s)')
	ylabel('voltage (mV)')
	title('About as simple as it gets, folks')
	grid(True)
	savefig("test.png")
	#show()
