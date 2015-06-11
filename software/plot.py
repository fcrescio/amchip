import sys
import glob, os
from utils import * 
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

def main(argv=["unknown.py"]):
	if len(argv) < 2:
		print "results_dicrectory\\prefix"
		sys.exit()

	silent = False
	if len(argv) > 2:
		silent = True

	namePrefix = argv[1]
	files = glob.glob(namePrefix+"*.res")

	if not silent:
		print files

	rv = []
	rf = []
	yv = []
	yf = []
	gv = []
	gf = []

	for f in files:
		res = UnPickle(f)

		print res["consumption"]
		err = res["err_rate"]
		error_rate = err[0]
		errors_total = err[2]
		volt = res["consumption"]["V"]
		freq = res["conf"]["real_freq"]

		if error_rate>0:
			if error_rate<10000:
				onFlyConclusion = 0.5
			else:
				onFlyConclusion = 0.0
		else:
			if errors_total>0:
				onFlyConclusion = 0.5
			else:
				onFlyConclusion = 1.0

		offlineRes = res["pattout_results"]
		offlineConclusion = 1.0 if len(offlineRes["extra"]) == 0 and len(offlineRes["missing"]) == 0 and len(offlineRes["wrongHitmap"]) == 0 else 0.0

		totalConclusion = onFlyConclusion * offlineConclusion

		if len(argv) > 2:
			if argv[2][0] == "f":
				totalConclusion = onFlyConclusion				
			if argv[2][0] == "o":
				totalConclusion = offlineConclusion				

		if totalConclusion<0.1:
			rv.append(volt)
			rf.append(freq)
		else:
			if totalConclusion<0.9:
				yv.append(volt)
				yf.append(freq)
			else:
				gv.append(volt)
				gf.append(freq)

	fig = plt.figure()
	mrksize = 30
	plt.plot(rv, rf, '.', color="red", markersize=mrksize)
	plt.plot(yv, yf, '.', color="yellow", markersize=mrksize)
	plt.plot(gv, gf, '.', color="green", markersize=mrksize)
	plt.xlabel('Voltage, V')
	plt.ylabel('Frequency, MHz')
	plt.title('Shmoo plot')
	plt.show()
	fig.savefig(namePrefix+"_Shmoo.png")

if __name__ == '__main__':
	main(sys.argv)
 
