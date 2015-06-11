import sys
import glob, os
from utils import * 
from random import * 
import matplotlib as mplt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from pylab import *

def convert(x, y, hist):
	return hist[x][y]

def main(argv=["unknown.py"]):
	if len(argv) < 2:
		print "results_dicrectory\\prefix"
		sys.exit()

	namePrefix = argv[1]
	files = glob.glob(namePrefix+"*.res")

	print files

	ChipSize = 2048
	hist=[[0]*8 for i in xrange(ChipSize) ]

	for f in files:
		res = UnPickle(f)

		print res["consumption"]

		expected = res["expected"]
		received = res["received"]
		events = []

		for i in  xrange(len(expected)):
			events.append(((expected[i]&0x00FF0000)>>16) | ((received[i]&0x00FF0000)>>8))
			expected[i] = expected[i]&0xFF00FFFF
			received[i] = received[i]&0xFF00FFFF
			exp = expected[i]
			recv = received[i]
			if exp != recv and (exp&0xFFFF) == (recv&0xFFFF):
				addr = exp&0xFFFF
				hitDiff = (exp ^ recv) >> 24
				for j in xrange(8):
					if (hitDiff >> j)&1==1:
						hist[addr][j] = hist[addr][j] + 1

	# x = randn(100000)
	# y = randn(100000)+5

	# hist2d(x, y, bins=40, norm=LogNorm())
	# colorbar()
	# show()

	pattern = np.linspace(0, ChipSize-1, ChipSize)
	layer = np.linspace(0, 7, 8)
	X,Y = np.meshgrid(pattern, layer)
	Z = X
	for i in xrange(ChipSize):
		for j in xrange(8):
			Z[j,i] = hist[i][j]

	fig = plt.figure()
	im = plt.imshow(Z)#, cmap=plt.cm.RdBu, vmin=abs(Z).min(), vmax=abs(Z).max(), extent=[0, 1, 0, 1])
	fig.savefig(namePrefix+"_Patterns_Map.png")

if __name__ == '__main__':
	main(sys.argv)
 
