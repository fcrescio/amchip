import sys
from time import *
import re
import vxi11

def main(argv=["unknown.py"]):
	if len(argv) > 1:
		if argv[1] == "-h":
			print "[new_voltage V]"
			sys.exit()

	voltageV = 0
	currentA = 0

	print("Connect to DC Power supply")
	instr = vxi11.Instrument("134.158.154.57")
	print(instr.ask("*IDN?"))

	try:
		if len(argv) > 1:
			volt = float(argv[1])
			if volt > 1.4:
				volt = 1.4
			instr.write(":VOLT %f"%(volt))
			instr.write(":OUTP ON")

		sleep(0.3)
		response = instr.ask(":FETC?")
		print(response)

		splitted = response.split(",")
		currentA = float(splitted[0][0:-1])
		voltageV = float(splitted[1][0:-1])

		print("Voltage: %f V"%(voltageV))
		print("Current: %f mA"%(currentA*1000))
		print("Power Consumption: %f mW"%(currentA*voltageV*1000))
	except Exception, e:
		print "problem"
		pass

	instr.close()

	return {"A" : currentA, "V" : voltageV}

if __name__ == '__main__':
	main(sys.argv)
