import math
from utils import * 

def EncodeDivider(divider):
	if divider <= 0 or divider > 63:
		print "Error. Divider", divider, "is not allowed! Please use values in range [1,63]."
		raise
	
	if divider == 1:
		return {"HighCount" : 1, "LowCount" : 1, "Edge" : 0, "NoCount" : 1}
	remainder = divider % 2
	count = int(math.floor(divider / float(2)))
	# print "divider", divider, "count", count, "remainder", remainder
	if remainder == 0:
		return {"HighCount" : count, "LowCount" : count, "Edge" : 0, "NoCount" : 0}
	else:
		return {"HighCount" : count, "LowCount" : count+1, "Edge" : 1, "NoCount" : 0}

def DecodeDivider(dividerStruct):
	divider = 0
	if dividerStruct["Edge"] == 0 and dividerStruct["NoCount"] == 1 and dividerStruct["HighCount"] == 1 and dividerStruct["LowCount"] == 1:
		divider = 1
	elif dividerStruct["NoCount"] == 0 and (dividerStruct["Edge"] == 0 or dividerStruct["Edge"] == 1):
		divider = dividerStruct["HighCount"] + dividerStruct["LowCount"]
	else:
		print "Unknown divider configuration", dividerStruct
		#raise
	return divider

def PrepareDividerReg(dividerStruct):
	return dividerStruct["Edge"] << 24 | dividerStruct["NoCount"] << 16 | dividerStruct["HighCount"] << 8 | dividerStruct["LowCount"]

def ParseDividerReg(reg):
	return {"HighCount" : (reg >> 8) & 0x3f, "LowCount" : reg & 0x3f, "Edge" : (reg >> 24) & 0x1, "NoCount" : (reg >> 16) & 0x1}

AMCHIP_CLOCK = 1
GTX_CLOCK = 2

class ClockManager:
	
	# d: 0 - default connection, others - externaly provided connection
	# verbosity: 0 - silent, 1 - general info, 2 - debug
	def __init__(self, clock=AMCHIP_CLOCK, d=0, verbosity=1):
		self.clock = clock
		self.d = d
		self.mul = [i for i in xrange(5, 21)]
		self.div = [i for i in xrange(1, 64)]
		self.verbosity = verbosity
		self.debug = self.verbosity == 2
		self.SetupConnection()
		
	def SetupConnection(self):
		if self.d == 0:
			self.d = GetUhalDevice()
		if self.clock == AMCHIP_CLOCK:
			self.CTRL_REG = self.d.getNode("AMCHIP_CLOCK_CONTROL_REG")
			self.STATUS_REG = self.d.getNode("AMCHIP_CLOCK_STATUS_REG")
			self.SPY_DIVIDER_REG = self.d.getNode("AMCHIP_SPY_DIVIDER_REG")
			self.FIRST_DIVIDER_REG = self.d.getNode("AMCHIP_FIRST_DIVIDER_REG")
		if self.clock == GTX_CLOCK:
			self.CTRL_REG = self.d.getNode("GTX_CLOCK_CONTROL_REG")
			self.STATUS_REG = self.d.getNode("GTX_CLOCK_STATUS_REG")
			self.SPY_DIVIDER_REG = self.d.getNode("GTX_SPY_DIVIDER_REG")
			self.FIRST_DIVIDER_REG = self.d.getNode("GTX_FIRST_DIVIDER_REG")
		self.CheckConnection()
	
	def CheckConnection(self):
		status = ReadREG(self.STATUS_REG, self.debug, title="ReadStatus")
		if status & 0xffff0000 == 0x12340000:
			if self.verbosity > 0:
				print "Connection established successfuly"
		else:
			print "Connection was not established"
			raise
		dividers = []
		for i in xrange(7):
			dividers.append(PrepareDividerReg(EncodeDivider(5)))
		WriteBlockREG(self.FIRST_DIVIDER_REG, dividers, 7, self.debug, title="WriteDefaultDividers", check=True)

	def PrintStatus(self):
		CTRL = ReadREG(self.CTRL_REG, self.debug, title="ReadCTRL")
		status = ReadREG(self.STATUS_REG, self.debug, title="ReadStatus")
		dividers = ReadBlockREG(self.FIRST_DIVIDER_REG, 7, self.debug, title="ReadDividers")
		spy = ReadREG(self.SPY_DIVIDER_REG, self.debug, title="ReadSpy")
		print "Status: trigger", (CTRL >> 16) & 0x1,  "state_id", (status >> 4) & 0xf, "RST_MMCM", (status >> 3) & 0x1, "SSTEP", (status >> 2) & 0x1, "SRDY", (status >> 1) & 0x1, "locked", status & 0x1
		print "Status: MUL_SEL_EN", (status >> 13) & 0x1, "DIV_SEL_EN", (status >> 12) & 0x1, "MULT_SELECT", (status >> 8) & 0xf
		for i in xrange(len(dividers)):
			print "Clock %d Divider %d (0x%x)"%(i, DecodeDivider(ParseDividerReg(dividers[i])), dividers[i])
		print "Spy divider", DecodeDivider(ParseDividerReg(spy))

	# clock: -1 - switch in circular mode, 0 <= others < 2 - select specified clock
	def SelectClock(self, clock = -1):
		CTRL = ReadREG(self.CTRL_REG, self.debug, title="ReadCTRL")
		if clock == -1:
			clock = ((CTRL & 0x1) + 1)%2
		elif clock < 0 or clock >= 2:
			print "Attempt to select clock number", clock, " but there are only 2 clocks available. Please choose one of: 0 or 1"
			raise
		WriteREG(self.CTRL_REG, MSet(CTRL, clock, 0x1), self.debug, title="SelectClock", check=True)

	# multiplier: -1 - switch in circular mode, 0 <= others <= 15 - select specified multiplier
	def SelectMultiplier(self, multiplier = -1):
		CTRL = ReadREG(self.CTRL_REG, self.debug, title="ReadCTRL")
		if multiplier == -1:
			multiplier = ((CTRL >> 8 & 0xf) + 1)%16
		elif multiplier < 0 or multiplier >= 16:
			print "Attempt to select unavailable multiplier", multiplier
			raise
		newCTRL = MSet(MSet(CTRL, 1 << 16, 1 << 16), multiplier << 8, 0xf << 8)
		WriteREG(self.CTRL_REG, newCTRL, self.debug, title="SelectMultiplier")

	# multiplier must be in range [5,20]
	def SetMultiplier(self, multiplier = 6):
		self.SelectMultiplier(multiplier-5)

	# divider: must be in range [1, 63]
	def SetDivider(self, divider):
		if divider < 1 or divider > 63:
			print "Attempt to set divider out of range [1,63]"
			raise
		CTRL = ReadREG(self.CTRL_REG, self.debug, title="ReadCTRL")
		mult = 5 + ((CTRL >> 8) & 0xf)
		newDividers = []
		for i in xrange(7):
			newDividers.append(PrepareDividerReg(EncodeDivider(mult)))
		newDividers[CTRL & 0x1] = PrepareDividerReg(EncodeDivider(divider))
		WriteBlockREG(self.FIRST_DIVIDER_REG, newDividers, 7, self.debug, title="WriteDividers", check=True)
		WriteREG(self.CTRL_REG, MSet(CTRL, 1 << 16, 1 << 16), self.debug, title="ApplyNewDividers")

	# freq : MHz
	def SetFrequency(self, freq):
		minErr = 100000
		optM = 0
		optD = 0
		for m in reversed(xrange(len(self.mul))):
			for d in xrange(len(self.div)):
				posFreq = 100.0 * self.mul[m] / self.div[d]
				err = abs(posFreq - freq)/freq
				if err < minErr:
					minErr = err
					optM = m
					optD = d
		self.SelectMultiplier(optM)
		self.SelectClock(0)
		self.SetDivider(self.div[optD])
		print "AMchip clock:" if self.clock == AMCHIP_CLOCK else "GTX clock:", "Asked %.1f MHz. Set %.1f MHz = 100 MHz * %d / %d. Error = %.3f %%." %(freq, 100.0*self.mul[optM]/self.div[optD], self.mul[optM], self.div[optD], 100.0*minErr)
		return {"Multiplier": self.mul[optM], "Divider": self.div[optD]}
