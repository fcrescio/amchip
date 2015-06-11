import sys
import vxi11

def main(argv=["unknown.py"]):
	if len(argv) > 1:
		if argv[1] == "-h":
			print "[voltage V (default 1.0 V)]"
			sys.exit()

	vold = 1
	try:
		if len(argv) > 1:
			volt = float(argv[1])
	except Exception, e:
		print "problem"
		pass

	print("Connect to DC Power supply")
	instr = vxi11.Instrument("134.158.154.57")
	print(instr.ask("*IDN?"))
	if volt > 1.4:
		volt = 1.4
	instr.write(":VOLT %f"%(volt))
	instr.write(":OUTP ON")
	print("Voltage: %s"%(instr.ask(":VOLT?")))
	instr.close()

if __name__ == '__main__':
	main(sys.argv)
