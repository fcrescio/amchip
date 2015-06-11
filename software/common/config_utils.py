from utils import * 
from JTAG import * 
from ClockManager import * 
from SERDES import * 

def SetFrequencyMHz(clock, frequency):
	c = 0
	if clock == "a":
		c = ClockManager(AMCHIP_CLOCK, d=0, verbosity=0)	
	elif clock == "g":
		c = ClockManager(GTX_CLOCK, d=0, verbosity=0)	
	else:
		print Error_("SetFrequencyMHz:: Please specify correctly the clock: a - for AMchip clock, g - for GTX clock")
		raise
	# c.PrintStatus()
	return c.SetFrequency(frequency)

def ResetGTX():
	WriteREG("SPY.CTRL", 6)
	WriteREG("SPY.HOLD_ADDR", 2**20)
	WriteREG("GTX.CTRL.RESET_GTX", 1)
	WriteREG("GTX.CTRL.SWING", 2)
	WriteREG("GTX.CTRL.ENABLED", 0)
	WriteREG("GTX.CTRL.RESET_GTX", 0)

def GTXSendPRBS():
	WriteREG("GTX.CTRL", (2<<28) | 0x2)

	instr = []
	instr.append(iPRBS_EN)
	instr.append(iPRBS_EN)
	instr.append(iPRBS_EN | iGOTO | iINFINITE)
	instr.append(iPRBS_EN | iADDR)
	instr.append(iPRBS_EN)

	Upload("GTX.HIT_INSTR", instr)
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)

	WriteREG("GTX.CTRL", (2<<28) | 0x1)

def ReadPRBSErr(runTime, silent):

	j = GetJTAG()
	s = SERDES(j)
	err = ReadREG("PATTOUT.PRBS_ERRORS_TOTAL")
	
	timePassed = 0
	count =0
	last = err
	offset = err
	tick = time()
	ToChipErr = 0
	toChipTotalErr = 0
	while timePassed < runTime or runTime == -1:
		count=count+1
		CTRL = ReadREG("GTX.CTRL")
		WriteREG("GTX.CTRL",  ASet(CTRL, 1, 1<<8))
		WriteREG("GTX.CTRL",  ASet(CTRL, 0, 1<<8))

		sleep(0.5)
		err = ReadREG("PATTOUT.PRBS_ERRORS_TOTAL")

		j.NewSession()
		s.SEL_REG(pattin0_pattout | SysConfReg, s.SysConfReg(SerDesMode = MODE_PRBS7))
		toChipErr_info = s.SEL_STAT(pattin0_pattout | SysStatReg)
		s.STAT()
		s.SEL_REG(pattin0_pattout | SysConfReg, s.SysConfReg(errRd32 = 1, errRd8 = 1, SerDesMode = MODE_PRBS7))
		s.SEL_STAT(pattout | SysStatReg)
		s.STAT()
		j.Dispatch()
		ToChipErr = j.Retrieve(toChipErr_info) & 0xffff
		toChipTotalErr = toChipTotalErr + AGet(ToChipErr, m_errDout32)
		if not silent:
			print "count", count, "ToChipErr", hex(toChipTotalErr), "\tErrors PATTOUT: %x"%(err-offset), "Rate: %d"%(err-last)
		if count==3:
			offset = err
			toChipTotalErr = 0
		last = err

		tock = time()
		timePassed = timePassed + tock - tick
		tick = tock
	return {"FromChip" : err-offset, "ToChip" : toChipTotalErr}

def ConfigureSerDes(mult, div, mode):
	WriteREG("GTX.CTRL.INIT", 1)
	WriteREG("GTX.CTRL.INIT", 0)

	j = GetJTAG()
	j.ResetAMchip()
	j.Dispatch()
	s = SERDES(j)
	s.Config(pattin0_pattout, mult, div, mode,
		s.RXTXConfReg2(DTestEnable = 1, RXTSel = 2, TXTSel = 2, RTrim = 2, RXTerm = 1, RXEn = 1, TXEn = 1),
		s.RXTXConfReg3(BandGapTrim = 2, DriveStrength = 3))

	s.Config(pattin1, mult, div, mode,
		s.RXTXConfReg2(DTestEnable = 1, RXTSel = 2, TXTSel = 2, RTrim = 2, RXTerm = 1, RXEn = 1, TXEn = 1),
		s.RXTXConfReg3(BandGapTrim = 2, DriveStrength = 3))

	for i in range(8):
		s.Config(bus0+i, mult, div, MODE_Normal,
			#s.RXTXConfReg2(RTrim = 2, RXTerm = 1, TXTerm = 1, RXEn = 1, TXEn = 1),
			s.RXTXConfReg2(DTestEnable = 1, RXTSel = 2, TXTSel = 2, RTrim = 2, RXTerm = 1, RXEn = 1, TXEn = 1),
			s.RXTXConfReg3(BandGapTrim = 2, DriveStrength = 2))

def simplify(mult_div):
	i = 2
	while i<=mult_div[0] and i <= mult_div[1]:
		if mult_div[0] % i == 0 and mult_div[1] % i == 0:
			mult_div[0] = mult_div[0] / i
			mult_div[1] = mult_div[1] / i
			i = 1
		i = i+1

class SpeedException(Exception):
	pass

def SetFreqMHzAndConfigSerDesGbps(AMchipFreqMHz = 100.0, SerDesSpeedGbps = 2.0, mode = MODE_Normal):
	AMchip_mult_div = SetFrequencyMHz("a", AMchipFreqMHz)
	GTX_mult_div = SetFrequencyMHz("g", 100.0 * SerDesSpeedGbps / 2.0)
	ResetGTX()

	real_freq = 100.0 * AMchip_mult_div["Multiplier"] / AMchip_mult_div["Divider"]
	real_speed = 2.0 * GTX_mult_div["Multiplier"] / GTX_mult_div["Divider"]

	mult = 20 * GTX_mult_div["Multiplier"] * AMchip_mult_div["Divider"]
	div = GTX_mult_div["Divider"] * AMchip_mult_div["Multiplier"]

	toSimplify = [mult, div]
	simplify(toSimplify)

	mult = toSimplify[0]
	div = toSimplify[1]

	if mult >= 255:
		print Error_("Impossible to find the appropriate multiplier for link speed %.5f at %.5f MHz reference clock."%(real_speed, real_freq))
		raise SpeedException(real_speed)

	while mult < 20:
		print Warning_("Multiplier %d is less than 20. Multiplying both by 2 (multiplier and divider)."%(mult))
		mult = mult * 2
		div = div * 2

	ConfigureSerDes(int(mult), int(div), mode)
	if mode == MODE_PRBS7:
		GTXSendPRBS()

	return {"aMult" : AMchip_mult_div["Multiplier"], "aDiv" : AMchip_mult_div["Divider"], 
			"gMult" : GTX_mult_div["Multiplier"], "gDiv" : GTX_mult_div["Divider"], 
			"sMult" : mult, "sDiv" : div, "real_freq" : real_freq, "real_speed" : real_speed}
