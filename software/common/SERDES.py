from utils import *

SERDES_SEL = 0xC9
SERDES_REG = 0xCA
SERDES_STAT = 0xEA

# SERDES_SEL which register
SysConfReg = 0x00
SysStatReg = SysConfReg
BISTConfReg = 0x10
BISTStatReg = BISTConfReg
RXTXConfReg0 = 0x20
RXTXConfReg1 = 0x30
RXTXConfReg2 = 0x40
RXTXConfReg3 = 0x50
SSModConfReg = 0x60

# SerDesMode Sel
MODE_Normal = 0x0
MODE_PRBS7 = 0x1
MODE_Pattern = 0x2
MODE_LoopBack = 0x3

# SERDES_SEL which serdes
pattin0_pattout = 0x00
pattout = pattin0_pattout
pattin0 = 0x01
pattin1 = 0x02
bus0 = 0x08
bus1 = 0x09
bus2 = 0x0a
bus3 = 0x0b
bus4 = 0x0c
bus5 = 0x0d
bus6 = 0x0e
bus7 = 0x0f

# SysConfReg bit fields
m_errRd32 = 0x1 << 12
m_errRd8 = 0x1 << 8
m_patSel = 0x7 << 4
m_SerDesMode = 0x3

# SysStatReg bit fields
m_TxStreamError = 0x1 << 28
m_RxStreamError = 0x1 << 24 # Bug - always 1
m_LinkUp32 = 0x1 << 20
m_LinkUp8 = 0x1 << 16
m_errDout32 = 0xff << 8
m_errDout8 = 0xff

# DTestOut sel
DTO_1b1 = 0x0
DTO_1b0 = 0x1
DTO_REFCLK = 0x2
DTO_clock_for_lock = 0x3
DTO_LOCK_pre_signal = 0x4
DTO_CLK40 = 0x5
DTO_CLK10 = 0x6
DTO_LOCK = 0x7

# RXTXConfReg0 bit fields
m_RxTxReset = 0x1 << 28
m_rx_txdiv = 0x0ff << 16 # Bug - actual width is 8 bit instead of 12 (note first 0)
m_rx_txpre = 0x1f << 8
m_HSSLEnable = 0x1 << 4
m_RxTxPD = 0x1

# RXTXConfReg1 bit fields
m_TXPPL_frac_ref_feedback_div = 0xffffff

# RXTXConfReg2 bit fields
m_DSMPD = 0x1 << 28
m_DTestEnable = 0x1 << 24
m_RXTSel = 0x7 << 20
m_TXTSel = 0x7 << 16
m_RTrim = 0x3 << 12
m_SelVDD = 0x1 << 8
m_RXTerm = 0x1 << 5
m_TXTerm = 0x1 << 4
m_RXEn = 0x1 << 1
m_TXEn = 0x1

# RXTXConfReg3 bit fields
m_BandGapTrim = 0xf << 4
m_DriveStrength = 0x3

# SSModConfReg bit fields
m_hard_vals_BIST = 0x1 << 20
m_down_spread = 0x1 << 16
m_spread = 0x1f << 8
m_divval = 0xf << 4
m_disable = 0x1

class SERDES:
	def __init__(self, jtag):
		self.j = jtag

	def SysConfReg(self, errRd32 = 0, errRd8 = 0, patSel = 0, SerDesMode = 0):
		return FSet(errRd32, m_errRd32) | FSet(errRd8, m_errRd8) | FSet(patSel, m_patSel) | FSet(SerDesMode, m_SerDesMode)

	def RXTXConfReg0(self, RxTxReset = 0, rx_txdiv = 0, rx_txpre = 0, HSSLEnable = 0, RxTxPD = 0):
		return FSet(RxTxReset, m_RxTxReset) | FSet(rx_txdiv, m_rx_txdiv) | FSet(rx_txpre, m_rx_txpre) | FSet(HSSLEnable, m_HSSLEnable) | FSet(RxTxPD, m_RxTxPD)

	def RXTXConfReg2(self, DSMPD = 0, DTestEnable = 0, RXTSel = 0, TXTSel = 0, RTrim = 0, SelVDD = 0, RXTerm = 0, TXTerm = 0, RXEn = 0, TXEn = 0):
		return FSet(DSMPD, m_DSMPD) | FSet(DTestEnable, m_DTestEnable) | FSet(RXTSel, m_RXTSel) | FSet(TXTSel, m_TXTSel) | FSet(RTrim, m_RTrim) | FSet(SelVDD, m_SelVDD) | FSet(RXTerm, m_RXTerm) | FSet(TXTerm, m_TXTerm) | FSet(RXEn, m_RXEn) | FSet(TXEn, m_TXEn)

	def RXTXConfReg3(self, BandGapTrim = 0, DriveStrength = 0):
		return FSet(BandGapTrim, m_BandGapTrim) | FSet(DriveStrength, m_DriveStrength)

	def SSModConfReg(self, hard_vals_BIST = 0, down_spread = 0, spread = 0, divval = 0, disable = 0):
		return FSet(hard_vals_BIST, m_hard_vals_BIST) | FSet(down_spread, m_down_spread) | FSet(spread, m_spread) | FSet(divval, m_divval) | FSet(disable, m_disable)

	def SEL(self, value):
		return self.j.access_register(SERDES_SEL, value, 7, "SERDES SEL")

	def REG(self, value):
		return self.j.access_register(SERDES_REG, value, 32, "SERDES REG")

	def SEL_REG(self, sel, reg):
		self.j.access_register(SERDES_SEL, sel, 7, "SERDES SEL")
		return self.j.access_register(SERDES_REG, reg, 32, "SERDES REG")

	def STAT(self, value = 0):
		return self.j.access_register(SERDES_STAT, value, 32, "SERDES STAT")

	def SEL_STAT(self, sel, reg = 0):
		self.j.access_register(SERDES_SEL, sel, 7, "SERDES SEL")
		return self.j.access_register(SERDES_STAT, reg, 32, "SERDES STAT")

	def Config(self, serdes, mult, div, mode, customRXTXConfReg2, customRXTXConfReg3):
		# Power down and configure
		self.j.NewSession()
		self.SEL_REG(serdes | RXTXConfReg0, self.RXTXConfReg0(RxTxReset = 1, rx_txdiv = mult, rx_txpre = div, RxTxPD = 1))
		self.SEL_REG(serdes | RXTXConfReg0, self.RXTXConfReg0(RxTxReset = 0, rx_txdiv = mult, rx_txpre = div, RxTxPD = 1))
		self.SEL_REG(serdes | SysConfReg, self.SysConfReg(SerDesMode = mode))
		self.SEL_REG(serdes | BISTConfReg, 0x00)
		self.SEL_REG(serdes | RXTXConfReg1, 0x00)
		self.SEL_REG(serdes | RXTXConfReg2, customRXTXConfReg2)
		self.SEL_REG(serdes | RXTXConfReg3, customRXTXConfReg3)
		self.SEL_REG(serdes | SSModConfReg, self.SSModConfReg(spread = 3, divval = 6, disable = 1))
		self.j.Dispatch()

		# Power up
		self.j.NewSession()
		self.SEL_REG(serdes | RXTXConfReg0, self.RXTXConfReg0(rx_txdiv = mult, rx_txpre = div, RxTxPD = 0))
		self.j.Dispatch()

		# Reset Stats
		self.j.NewSession()
		self.SEL_STAT(serdes | SysStatReg)
		self.SEL_STAT(serdes | BISTStatReg)
		self.j.Dispatch()
