import math
from random import *
import sys
from test_utils import * 

def main(argv="unknown.py"):
	if len(argv) < 2:
		print "mode (l - for loop channels mode, s - for single channel mode) [channel (if single channel mode) [repeat] ]"
		sys.exit()
	if argv[1][0] == "l":
		loopMode = 1
	elif argv[1][0] == "s":
		loopMode = 0
	else:
		print Error_("Please specify correctly the mode (l - for loop channels mode, s - for single channel mode)")
		raise

	if len(argv) > 2:
		channel = int(argv[2])
	else:
		channel = 0

	if channel < 0 or channel > 7:
		print Error_("Please specify correctly the channel (available channels are 0-7)")
		raise

	if len(argv) > 3:
		repeat = int(argv[5])
	else:
		repeat = 0

	sclkDivider = 3
	delay = 2
	if len(argv) > 3:
		sclkDivider = int(argv[3])
	if len(argv) > 4:
		delay = int(argv[4])

	a = GetADC()
	CTRL = a.PrepareCTRL(sclkDivider = sclkDivider, delay = delay, repeat=repeat, loopChannels = loopMode)
	CONFIG = a.PrepareConfig(ChAddr=channel)
	ReadADC(CTRL, CONFIG)

	n = 1000
	vals = []
	t = Tick()
	for i in xrange(n):
		vals.append(JustReadADC())
	Tock(t, "%d samples"%(n))
	mean = [0]*8
	devsqr = [0]*8
	dev = [0]*8
	for i in xrange(n):
		for ch in xrange(8):
			mean[ch] = mean[ch]+(vals[i][ch] & 0xFFF)
	for ch in xrange(8):
		mean[ch] = float(mean[ch])/float(n)
	for i in xrange(n):
		for ch in xrange(8):
			devsqr[ch] = devsqr[ch]+((vals[i][ch] & 0xFFF) - mean[ch])**2
	for ch in xrange(8):
		dev[ch] = math.sqrt(float(devsqr[ch])/float(n))

	chNames = [ "VDD_SERDES",
				"VDD_CORE  ",
				"VDD_FC    ",
				"VDDH      ",
				"VDD_IO    ",
				"VDDA_BGREF",
				"VDDA_LVDS ",
				"VDDA      "]
	for ch in xrange(8):
		if mean[ch]<0.000001:
			mean[ch] = 0.00001
		print "CH%d - %s \tValue = %x = %f Vref std = %f = %f %%"%(ch, chNames[ch], mean[ch], mean[ch]/(2.0**12), dev[ch]/(2.0**12), 100.0*dev[ch]/mean[ch])

if __name__ == '__main__':
	if len(sys.argv) > 1:
		if sys.argv[1] == "li" or sys.argv[1] == "si":
			while True:
				main(sys.argv)
	main(sys.argv)
