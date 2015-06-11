from utils import * 

# SPI Controller CTRL
m_spi_repeat = 0xFF << 24
m_spi_sclk_divider = 0xFF << 16
m_spi_delay = 0xFF << 8
m_spi_loop_channels = 0x1 << 2
m_spi_operation_enabled = 0x1 << 1
m_spi_reconfigure = 0x1

# SPI Controller CONFIG
m_spi_adc_config = 0xFFFF


ADC_ManualMode = 1

# ADC SDI
m_adc_mode = 0xF << 12
m_adc_enable_programming = 0x1 << 11
m_adc_channel_addr = 0xF << 7
m_adc_range = 0x1 << 6
m_adc_power_down = 0x1 << 5
m_adc_output_GPOI_instead_of_channel_addr = 0x1 << 4
m_adc_GPIO_data = 0xF

class ADC:
	
	# verbosity: 0 - silent, 1 - general info, 2 - debug
	def __init__(self, verbosity):
		self.SetVerbosity(verbosity)

	def SetVerbosity(self, verbosity):
		self.v = verbosity
		self.debug = verbosity == 2

	def GetVerbosity(self):
		return self.v

	def PrepareConfig(self, Mode=ADC_ManualMode, EnProgramming=0, ChAddr=0, Range=0, PowerDown=0, GPOIinsteadChAddr=0, GPIOdata=0):
		return (FSet(Mode, m_adc_mode) | FSet(EnProgramming, m_adc_enable_programming)
		| FSet(ChAddr, m_adc_channel_addr) | FSet(Range, m_adc_range) | FSet(PowerDown, m_adc_power_down)
		| FSet(GPOIinsteadChAddr, m_adc_output_GPOI_instead_of_channel_addr) | FSet(GPIOdata, m_adc_GPIO_data))

	def PrepareCTRL(self, sclkDivider = 0x3, delay = 0x2, repeat = 0, loopChannels = 1, operationEnabled = 1, reconfigure = 1):
		return (FSet(repeat, m_spi_repeat) | FSet(sclkDivider, m_spi_sclk_divider) | FSet(delay, m_spi_delay) | FSet(loopChannels, m_spi_loop_channels)
		| FSet(operationEnabled, m_spi_operation_enabled) | FSet(reconfigure, m_spi_reconfigure))

	def PrintStatus(self):
		s = ReadREG("ADC.STATUS", self.debug, "ReadSTATUS")
		print "Status: spi_enable=%d spi_busy=%d spare_out=%x spare_in=%x"%(FGet(s, 0x1 << 16), FGet(s, 0x1 << 12), FGet(s, 0xFF << 4), FGet(s, 0x3))

	def ReadVal(self, userCTRL="no", userCONFIG="no"):
		if userCTRL == "no":
			CTRL = self.PrepareCTRL()
		else:
			CTRL = userCTRL
		if userCONFIG == "no":
			CONFIG = self.PrepareConfig()
		else:
			CONFIG = userCONFIG
		WriteREG("ADC.CTRL", CTRL, self.debug, "WriteCTRL")
		WriteREG("ADC.CONFIG", CONFIG, self.debug, "WriteCONFIG")
		# After disabling loopChannels channel will be reset to 0 automatically, so you need to set it again
		WriteREG("ADC.CTRL", CTRL, self.debug, "WriteCTRL")
		WriteREG("ADC.CONFIG", CONFIG, self.debug, "WriteCONFIG")
		if self.v > 0:
			ReadREG("ADC.CTRL", self.debug, "ReadCTRL")
			self.PrintStatus()
		return ReadBlockREG("ADC.CH0", 8, self.debug, "ReadChannels")

	def JustReadVal(self):
		return ReadBlockREG("ADC.CH0", 8, self.debug, "ReadChannels")

 
ADCInstance = 0
defaultVerbosityADC = 0 # 0 - no output, 1 - general info, 2 - debug

def GetADC(verbosity = -1):
	global ADCInstance
	if ADCInstance == 0:
		ADCInstance = ADC(defaultVerbosityADC)
	if verbosity >=0:
		ADCInstance.SetVerbosity(verbosity)
	else:
		ADCInstance.SetVerbosity(defaultVerbosityADC)
	return ADCInstance
