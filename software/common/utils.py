import os.path
import uhal
import pickle
from time import *
from random import *

def randuint32():
	return randint(0, 0xffffffff)

ticks = {}

def Tick(label = ""):
	if label == "":
		label = str(len(ticks))
	ticks[label] = time()
	return label

def Tock(label, title = ""):
	time_passed = time() - ticks[label]
	if title != "":
		print title, "took %f seconds"%(time_passed)
	return time_passed

# Instructions

iINFINITE = 0xFFFFFF

opcode_nothing = 0x0
opcode_threshold8_8 = 0x1
opcode_threshold7_8 = 0x2
opcode_threshold6_8 = 0x3
opcode_init = 0x5
opcode_decrese_threshold = 0x7
opcode_threshold0_8 = 0xA
opcode_threshold9_8 = 0xB
opcode_toggle_mandatory_0 = 0xE

iIDLE = 0
iSAMPLE_ADC = 0x1 << 23;
iDATA = 0x1 << 24;
iOPCODE = 0x1 << 25;
iPRBS_EN = 0x1 << 26;
iPRBS_FORCE_ERR = 0x1 << 27;
iHOLD_PATTOUT_FLAG = 0x1 << 28;
iADDR = 0x1 << 29;
iALLIGN_PREDICTED = 0x1 << 30
iGOTO = 0x1 << 31

# Colorful output

c_HEADER = '\033[95m'
c_OKBLUE = '\033[94m'
c_GREEN = '\033[92m'
c_WARNING = '\033[93m'
c_FAIL = '\033[91m'
c_ENDC = '\033[0m'
c_BOLD = '\033[1m'
c_UNDERLINE = '\033[4m'

def Ok_(s):
	return c_GREEN + s + c_ENDC

def Error_(s):
	return c_FAIL + s + c_ENDC

def Warning_(s):
	return c_WARNING + s + c_ENDC

def Header_(s):
	return c_HEADER + s + c_ENDC

# Bit manipulation functions

def change_nth_bit(value, n):
	oldBit = (value >> n) & 1;
	if oldBit:
		return value & (~(1 << n))
	else:
		return value | (1 << n)

def MaskedSet(reg, value, mask):
	reg &= ~mask
	value &= mask
	reg |= value
	return reg

def MSet(reg, value, mask):
	return MaskedSet(reg, value, mask)

def AutoSet(reg, value, mask):
	lsb = 0
	while(lsb < 32 and (mask >> lsb ) & 0x1 == 0):
		lsb = lsb + 1
	if lsb == 32:
		print Error_("AutoSet: Empty mask provided")
		raise
	return MaskedSet(reg, value << lsb, mask)

def ASet(reg, value, mask):
	return AutoSet(reg, value, mask)

def AutoGet(reg, mask):
	lsb = 0
	while(lsb < 32 and (mask >> lsb ) & 0x1 == 0):
		lsb = lsb + 1
	if lsb == 32:
		print Error_("AutoSet: Empty mask provided")
		raise
	msb = lsb
	while(msb < 32 and (mask >> msb) & 0x1 == 1):
		msb = msb + 1
	return (reg >> lsb) & (2**(msb-lsb)-1)

def AGet(reg, mask):
	return AutoGet(reg, mask)

def FieldSet(value, mask):
	return ASet(0, value, mask)

def FSet(value, mask):
	return FieldSet(value, mask)	

def FGet(reg, mask):
	return AutoGet(reg, mask)

# IPBus setup

uhalDevice = 0

def FileExists(filename):
	return os.path.isfile(filename) 

def GetUhalDevice(LogLevel = uhal.LogLevel.WARNING):
	uhal.setLogLevelTo(LogLevel)
	global uhalDevice
	if uhalDevice == 0:
		f = "addresses.xml"
		if not FileExists(f):
			f = "common/addresses.xml"
		if not FileExists(f):
			f = "../common/addresses.xml"
		if not FileExists(f):
			print Error_("Could not find file \"addresses.xml\"")
			raise
		uhalDevice = uhal.getDevice("fpga", "ipbusudp-2.0://134.158.152.64:50001", "file://"+f)
		# print "Creating device"
	return uhalDevice

# IPBus Distributed RAM access functions

def WriteREG(register, data, debug=False, title="WriteRegister", clear=False, check=False):
	d = GetUhalDevice()
	if type(register) is str:
		register = d.getNode(register)
	if clear:
		send_data = 0x00000000
	else:
		send_data = data
	response = []
	register.write(send_data)
	response = register.read()
	d.dispatch()
	if debug:
		print title, hex(response)
	if send_data!=response:
		if debug:
			print title, "Wronge response."
		if check:
			raise

def ReadREG(register, debug=False, title="ReadRegister"):
	d = GetUhalDevice()
	if type(register) is str:
		register = d.getNode(register)
	response = []
	response = register.read()
	d.dispatch()
	if debug:
		print title, hex(response)
	return int(response)

def WriteBlockREG(register, data, size, debug=False, title="WriteBlockRegister", clear=False, check=False):
	d = GetUhalDevice()
	if type(register) is str:
		register = d.getNode(register)
	if clear:
		send_data = [0]*size
	else:
		send_data = data[0:size]
	response = []
	register.writeBlock(send_data)
	response = register.readBlock(size)
	d.dispatch()
	if debug:
		for i in range(size):
			print title, i, hex(response[i])
	for i in range(size):
		if send_data[i]!=response[i]:
			if debug:
				print title, "Wronge response at", i
			if check:
				raise

def ReadBlockREG(register, size, debug=False, title="ReadBlockRegister"):
	d = GetUhalDevice()
	if type(register) is str:
		register = d.getNode(register)
	response = []
	response = register.readBlock(size)
	d.dispatch()
	if debug:
		for i in range(size):
			print title, i, hex(response[i])
	return [x for x in response]

# IPBus Block RAM access functions

def EventsToList(events):
	stream = []
	for x in events:
		stream.extend(x)
	return stream

def Check(title, addr_width, size, offset):
	ram_size = 2**addr_width
	if offset<0 or offset > ram_size-1:
		print Error_("Offset %d exceeds allowed range [%d, %d] of %s"%(offset, 0, ram_size-1, title))
		raise
	if size<1 or size > ram_size:
		print Error_("Size %d exceeds allowed range [%d, %d] of %s"%(size, 1, ram_size, title))
		raise
	if offset + size > ram_size:
		print Error_("Offset+Size %d overflows memory size %d of %s"%(offset + size, ram_size, title))
		raise

def Dump(name, size = -1, offset = 0):
	d = GetUhalDevice()
	ptr_name = name + "_PTR"
	mem_name = name + "_MEM"
	ptr=d.getNode(ptr_name)
	mem=d.getNode(mem_name)
	sizes = ptr.read()
	d.dispatch()
	data_width = (sizes >> 26) & 0x3f
	addr_width = (sizes >> 20) & 0x3f
	if size < 0:
		size = 2**addr_width
	# print name, "data_width", data_width, "addr_width", addr_width
	Check(name + " during dump", addr_width, size, offset)
	ptr.write(offset)
	dump = mem.readBlock(size)
	d.dispatch()

	stream = [x for x in dump]
	return stream

def Upload(name, data, offset = 0):
	d = GetUhalDevice()
	ptr_name = name + "_PTR"
	mem_name = name + "_MEM"
	ptr=d.getNode(ptr_name)
	mem=d.getNode(mem_name)
	sizes = ptr.read()
	d.dispatch()
	data_width = (sizes >> 26) & 0x3f
	addr_width = (sizes >> 20) & 0x3f
	# print name, "data_width", data_width, "addr_width", addr_width
	Check(name + " during upload", addr_width, len(data), offset)
	ptr.write(offset)
	mem.writeBlock(data)
	ptr.write(0)
	d.dispatch()

def Clear(name):
	d = GetUhalDevice()
	ptr_name = name + "_PTR"
	mem_name = name + "_MEM"
	ptr=d.getNode(ptr_name)
	mem=d.getNode(mem_name)
	sizes = ptr.read()
	d.dispatch()
	data_width = (sizes >> 26) & 0x3f
	addr_width = (sizes >> 20) & 0x3f
	offset = 0
	data = [0]*(2**addr_width)
	ptr.write(offset)
	mem.writeBlock(data)
	ptr.write(0)
	d.dispatch()

# Test IPBus speed using ram ...

def CheckSpeed(name, size):
	d = GetUhalDevice()
	ptr_name = name + "_PTR"
	mem_name = name + "_MEM"
	ptr=d.getNode(ptr_name)
	mem=d.getNode(mem_name)
	tick = time()
	ptr.write(0)
	# d.dispatch()
	repeat = 20
	for i in xrange(repeat):
		dump = mem.readBlock(size)
	# d.dispatch()
	# ptr.write(0)
	d.dispatch()
	tock = time()
	mem = repeat * size*32.0/(8.0*1024.0*1024.0)
	t = tock - tick
	print "Check speed with %f MB took %f sec. Speed %f MB/s"%(mem, t, mem/t)

# Pickle shortcuts

def Pickle(name, data):
	with open(name,'wb') as f:
		pickle.dump(data, f, -1)

def UnPickle(name):
	with open(name, 'rb') as f:
		return pickle.load(f)
