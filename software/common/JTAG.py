from time import *
from utils import *

# Access AMchip ------------------------------

def ResetAMchip(all_commands, debug=False, title="ResetAMchip"):
	commands = [4, 0]
	info = {"Beginning" : len(all_commands), "Size" : len(commands)}
	all_commands.extend(commands)
	return info

def access_instruction(all_infos, all_commands, IR, debug=False, title="AccessInstruction"):
	# go to shift IR
	commands = []
	commands.extend([2, 2, 0, 8])
	# send IR
	for i in range(7):
		if (IR>>i)&0x1 == 0:
			commands.append(8)
		else:
			commands.append(9)
	# send last IR bit and go to shift DR
	if (IR>>7)&0x1 == 0:
		commands.extend([2, 2, 0])
	else:
		commands.extend([3, 2, 0])
	info = {"Action" : "AccessInstruction", "Beginning" : len(all_commands), "Size" : len(commands), "Title" : title}
	all_commands.extend(commands)
	all_infos.append(info)
	return info

def retrieve_instruction(info, results, debug=False):
	first = info["Beginning"]
	title = info["Title"]
	read = 0
	read = read + 3
	tdo = 0
	tdo = tdo + results[first+read]
	read = read + 1
	for i in range(7):
		tdo = tdo + (results[first+read]<<(i+1))
		read = read + 1
	if tdo != 1:
		print title, "ERROR during IR set"
	read = read + 3
	if read!=info["Size"]:
		print title, "Mismatch of jtag commands and results count", info["Size"], read
	return tdo

def access_register(all_infos, all_commands, IR, DR, length = 32, debug=False, title="AccessRegister"):
	commands = []
	commands.extend([2, 2, 0, 8])
	for i in range(7):
		if (IR>>i)&0x1 == 0:
			commands.append(8)
		else:
			commands.append(9)
	if (IR>>7)&0x1 == 0:
		commands.append(0xA)
	else:
		commands.append(0xB)
	commands.extend([2, 2, 0, 8])
	for i in range(length-1):
		if (DR>>i)&0x1 == 0:
			commands.append(8) 
		else:
			commands.append(9)
	if (DR>>(length-1))&0x1 == 0:
		commands.append(0xA) 
	else:
		commands.append(0xB)
	commands.extend([2,0])
	info = {"Action" : "AccessRegister", "Beginning" : len(all_commands), "Size" : len(commands), "Length" : length, "Title" : title}
	all_commands.extend(commands)
	all_infos.append(info)
	return info

def retrieve_register(info, results, debug=False):
	first = info["Beginning"]
	length = info["Length"]
	title = info["Title"]
	read = 0
	read = read + 3
	tdo = results[first+read]
	read = read + 1
	for i in range(7):
		tdo = tdo + (results[first + read]<<(i+1))
		read = read + 1
	read = read + 1
	if tdo != 1:
		print title, "ERROR during IR set"
	read = read + 3
	tdo = results[first+read]
	read = read + 1
	for i in range(length-1):
		tdo = tdo + (results[first+read]<<(i+1))
		read = read + 1
	read = read + 1
	if debug:
		print(title+":\t%x"%(tdo))
	read = read + 2
	if read!=info["Size"]:
		print title, "Mismatch of jtag commands and results count", info["Size"], read
	return tdo

def access_long_register(all_infos, all_commands, IR, DR, length, debug=False, title="AccessLongRegister"):
	commands = []
	length_copy = length
        num_words = length//32
        if length%32:
                num_words = num_words + 1
	DR = list(DR)
	DR.reverse()
	commands.extend([2, 2, 0, 8])

	for i in range(7):
		if (IR>>i)&0x1 == 0:
			commands.append(8)
		else:
			commands.append(9)
	if (IR>>7)&0x1 == 0:
		commands.append(0xA)
	else:
		commands.append(0xB)
	commands.extend([2, 2, 0, 8])
	j = 0
	for j in range(num_words):
		cur_length = 0
		if j < (num_words - 1):
			cur_length = 32
		else:
			cur_length = length-1
		if (j < (num_words - 1)):
			length -= 32
		for i in range(cur_length):
			if (DR[j]>>i)&0x1 == 0:
				commands.append(8)
			else:
				commands.append(9)
	if (DR[j]>>(length-1))&0x1 == 0:
		commands.append(0xA)
	else:
		commands.append(0xB)
	commands.extend([2, 0])
	info = {"Action" : "AccessLongRegister", "Beginning" : len(all_commands), "Size" : len(commands), "Length" : length_copy, "Title" : title}
	all_commands.extend(commands)
	all_infos.append(info)
	return info

def retrieve_long_register(info, results, debug=False):
	first = info["Beginning"]
	length = info["Length"]
	title = info["Title"]
	read = 0
	num_words = length//32
	if length%32:
		num_words = num_words + 1
	read = read + 3
	tdo = 0
	tdo = tdo + results[first+read]
	read = read + 1
	for i in range(7):
		tdo = tdo + (results[first+read]<<(i+1))
		read = read + 1
	read = read + 1
	if tdo != 1:
		print title, "ERROR during IR set"
	read = read + 3
	tdo = []
	j = 0
	for j in range(num_words):
		cur_length = 0
		if j < (num_words - 1):
			cur_length = 32
		else:
			cur_length = length
		if j >= 0:
			tdo.append(0)
			tdo[len(tdo)-1] = tdo[len(tdo)-1] + results[first+read]
			read = read + 1
		if (j < (num_words - 1)):
			length -= 32
		for i in range(cur_length-1):
			tdo[j] = tdo[j] + (results[first+read]<<(i+1))
			read = read + 1
		if debug:
			print(title+":\t%d %x"%(j,tdo[j]))
	read = read + 1
	read = read + 2
	if read!=info["Size"]:
		print title, "Mismatch of jtag commands and results count", info["Size"], read
	return tdo

def retrieve(info, all_results, debug=False, title="RetrieveInfo"):
	res = 0
	if info["Action"]=="AccessInstruction":
		res = retrieve_instruction(info, all_results, debug)
	if info["Action"]=="AccessRegister":
		res = retrieve_register(info, all_results, debug)
	if info["Action"]=="AccessLongRegister":
		res = retrieve_long_register(info, all_results, debug)
	return res	

def RetrieveInfos(infos, all_results, debug=False, title="RetrieveInfos"):
	results = []
	for i in range(len(infos)):
		results.append(retrieve(infos[i], all_results, debug))
	return results

def jpatt_ctrl_gen( thr = 0xF, reqlay = 0x0, geoaddr = 0x0, disabled = 0x0, delay = 0x0, bottom = 0x0, layer12 = 0x0, blmode = 0x0, tmode = 0x0, laymap = 0x0, last = 0x0, disableFlow = 0x0, jtagclk = 0x0, strength = 0x0, rtcal = 0x0, dcbits = 0x0, continuous = 0x0):
	words = []
	words.append( thr&0xf | (reqlay&0x1)<<4 | (geoaddr&0x3f) << 8 | (disabled&0x3)<<16 | (delay&0x7)<<28 )
	words.append( (bottom&0x1) | (layer12&0x1)<<4 | (blmode&0x1)<<5 | (tmode&0x1)<<8 | (laymap&0x1)<<12 | (last&0x1)<<16 | (disableFlow&0x1)<<20 | (jtagclk&0x1)<<24 | (strength&0x1)<<28 | (rtcal&0x3)<<29 )
	#words.append( (dcbits&0xffff) | (continuous&0x1)<<16 )
	words.append( (dcbits&0xffffffff) )
	words.append( (continuous&0x1) )
	words.reverse()
	return words

def my_pack_to_32bit(values, lengths):
	packed = []
	offset = 0
	for element in range(len(lengths)):
		data = values[element]
		i = 0
		w = 0
		while (i+32*w<lengths[element]):
			if offset==0:
				packed.append(0)
			packed[len(packed)-1] |= ((data[w]>>i)&0x1)<<offset
			if i<31:
				i += 1
			else:
				i = 0
				w += 1
			if offset<31:
				offset += 1
			else:
				offset = 0
	return packed		
	
def pack_to_32bit(values, lengths):
	packed = []
	offset = 0
	word = 0
	elements = len(lengths)
	for element in range(elements):
		nwords = lengths[element] // 32
		for i in range(nwords):
			if offset > 0:
				packed[len(packed) - 1] |= (values[element][i] & (0xffffffff >> (offset)))<<offset
				packed.append(values[element][i] >> (32-offset))
			else:
				packed.append(values[element][i])
		if (lengths[element] % 32) > 0:
			if offset > 0:
				packed[len(packed) - 1] |= (values[element][nwords] & (0xffffffff >> (offset)))<<offset
				if offset + (lengths[element]%32) > 32:
					newoffset = (offset + (lengths[element]%32))%32
					packed.append(values[element][nwords] >> (32-newoffset))
			else:
				packed.append(values[element][nwords])
			offset = (offset + (lengths[element]%32))%32
	return packed	
	
def pack_jdata(pattern, disable=True):
	patt_list = []
	for word in pattern:
		patt_list.append([word])
	if disable:
		disable_bit = [1]
	else:
		disable_bit = [0]
	patt_list.append(disable_bit)
	mylist = my_pack_to_32bit(patt_list,[18,18,18,18,18,18,18,18,1]) 
	mylist.reverse()
	return mylist
	
def GetIDCODE(all_infos, all_commands):	
	return access_register(all_infos, all_commands, IR=0x1, DR=0x0, title="GetIDCODE")
	
def SetChipSetup(all_infos, all_commands, ChipSetup):	
	return access_long_register(all_infos, all_commands, 0xC6, ChipSetup, 97, title="SetChipSetup")

def GetChipSetup(all_infos, all_commands):	
	return access_long_register(all_infos, all_commands, 0xE6,[0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF],97, title="GetChipSetup")

def InitEvent(all_infos, all_commands):
	return access_instruction(all_infos, all_commands, 0xD6, title="InitEvent")

def SetPatternAddress(all_infos, all_commands, address):
	return access_register(all_infos, all_commands, 0xC4, address,16, title="SetPatternAddress")

def GetPatternAddress(all_infos, all_commands):
	return access_register(all_infos, all_commands, 0xE4, 0x0,16, title="GetPatternAddress")

def WriteAndIncreasePatternAddress(all_infos, all_commands):
	return access_instruction(all_infos, all_commands, 0xD4, title="IncreasePatternAddress")

def AccessRecAddress(all_infos, all_commands):
	return access_register(all_infos, all_commands,0xE8,0x0,25, title="AccessRecAddress")

def PrepareNextRecAddress(all_infos, all_commands):
	return access_instruction(all_infos, all_commands, 0xD5, title="PrepareNextRecAddress")

def SetIdleConfig(all_infos, all_commands, config):
	return access_register(all_infos, all_commands, 0xCB, config, title="SetIdleConfig")

def PrintRecAddress(info, all_results):
	res = retrieve_register(info, all_results)
	if res&0x1 == 1:
		print("Pattern %x Bitmap %x"%((res>>1)&0xffff, (res>>17)&0xff))

def SaveRecAddress(f, info, all_results):
	res = retrieve_register(info, all_results)
	if res&0x1 == 1:
		f.write(str("Pattern "+hex((res>>1)&0xffff)+" Bitmap "+hex((res>>17)&0xff))+"\n")

def PutDataOnBus(all_infos, all_commands, data, disabled):
	return access_long_register(all_infos, all_commands, 0xC5,pack_jdata(data, disabled),145, title="PutDataOnBus")

def ReadDataFromBus(all_infos, all_commands):
	return access_long_register(all_infos, all_commands, 0xE5,pack_jdata([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF], True),145, title="ReadDataFromBus")

# JTAG ------------------------------

def StrToComList(s):
	data = []
	for i in range(len(s)):
		data.append(int(s[i], 16))
	return data

def DeliverJTAG_Commands(d, JTAG_COMS_REG, commands, count, debug=False, title="DeliverJTAG_Commands"):
	# CheckSpeed(d, "JTAG.COMMANDS_RAM", 32000)
	data = []
	response = []
	merged = 0
	i = 0
	n = 0
	while merged<count:
		data.append(0x00000000)
		n = n+1
		i = 0
		while (merged<count) and (i<8):
			data[n-1] = data[n-1]|(commands[(n-1)*8+i]<<4*i)
			merged = merged + 1
			i = i +1
		while (i<8):
			data[n-1] = data[n-1]|(0xF<<4*i)
			i = i +1
	# JTAG_COMS_REG.writeBlock(data)
	# response = JTAG_COMS_REG.readBlock(n)
	tick = time()
	Upload("JTAG.COMMANDS", data)
	tock = time()
	mem = count*4.0/(8.0*1024.0*1024.0)
	t = tock - tick
	# print "Upload %d commands = %f MB took %f sec. Speed %f MB/s"%(count, mem, t, mem/t)
	# response = Dump(d, "JTAG.COMMANDS_RAM", len(data))
	d.getNode("JTAG.COMMANDS_AMOUNT").write(len(data))
	d.getNode("JTAG.STATUS").write(0)
	d.getNode("JTAG.CTRL").write(0)
	d.dispatch()
	if debug:
		for i in range(len(data)):
			print title, i, hex(data[i])
	# if debug:
	# 	for i in range(len(data)):
	# 		print title, i, hex(response[i])
	# for i in range(len(data)):
	# 	if data[i]!=response[i]:
	# 		print title, "Wronge response at", i
	# 		raise

def ExecuteJTAG_Commands(d, CONTROL_REG, JTAG_COM_COUNT_REG, N, debug=False, title="ExecuteJTAG_Commands"):
	# JTAG_COM_COUNT_REG.write(N)
	CONTROL_REG.write(0x00000001) # bit(0) - trigger jtag (is automatically reset to 0)
	# count_resp = JTAG_COM_COUNT_REG.read()
	control_resp = CONTROL_REG.read()
	d.dispatch()
	if debug:
		# print title, "Count REG", count_resp
		print title, "Control REG", control_resp

def ReadoutJTAG_Results(d, STATUS_REG, JTAG_RESULTS_REG, count, debug=False, title="ReadoutJTAG_Results"):
	N = count//8
	if count%8!=0:
		N = N+1
	tick = time()
	data_is_valid = False
	while not data_is_valid:
		# sleep(0.001)
		valid = STATUS_REG.read()
		d.dispatch()
		data_is_valid = (valid&1)==1
		if not data_is_valid:
			if debug:
				pass
				print title, "Data is not valid yet. Retry ..."
	tock = time()
	# print "Waiting about %f seconds for data to become valid"%(tock-tick)
	results = Dump("JTAG.COMMANDS", N)
	if debug:
		for i in range(N):
			print title, i, hex(results[i])
	data = []
	splitted = 0
	word = 0
	while splitted<count:
		i = 0
		while (splitted<count) and (i<8):
			data.append(0x0000000F & (results[word]>>4*i))
			splitted = splitted + 1
			i = i + 1
		word = word + 1;
	return data

def JTAG_Session(d, commands, buf_size, debug=False, title="JTAG_Session"):
	results = []
	processed = 0
	packs_sent = 0
	while processed<len(commands):
		pack_size = 0
		if len(commands)-processed<buf_size:
			pack_size = len(commands)-processed
		else:
			pack_size = buf_size
		DeliverJTAG_Commands(d, d.getNode(""), commands[processed:processed+pack_size], pack_size, debug)
		ExecuteJTAG_Commands(d, d.getNode("JTAG.CTRL"), d.getNode(""), pack_size, debug)
		pack_results = ReadoutJTAG_Results(d, d.getNode("JTAG.STATUS"), d.getNode(""), pack_size, debug)
		results.extend(pack_results)
		processed = processed + pack_size
		packs_sent = packs_sent + 1
		if debug:
			pass
			print title, ":", packs_sent, "JTAG packets sent"
	return results

class JTAG:
	
	# verbosity: 0 - no output, 1 - general info, 2 - debug
	def __init__(self, buf_size, verbosity):
		self.d = GetUhalDevice()
		self.SetVerbosity(verbosity)
		self.buf_size = buf_size
		self.NewSession()
	
	def SetVerbosity(self, verbosity):
		self.v = verbosity
		self.debug = verbosity == 2

	def GetVerbosity(self):
		return self.v

	def NewSession(self):
		self.all_commands = []
		self.all_results = []
		self.all_infos = []

	def Dispatch(self):
		start = time()
		if self.v>0:
			print "JTAG::Dispatch:", len(self.all_commands), "JTAG commands in total"
		self.all_results = JTAG_Session(self.d, self.all_commands, self.buf_size, self.debug)
		end = time()
		if self.v>0:
			print "JTAG::Dispatch: It took me", end-start, "seconds."
		if self.debug:
			self.PrintResults()
	
	def PrintResults(self):
		RetrieveInfos(self.all_infos, self.all_results, debug=True, title="RetrieveInfos")

	# Access AMchip functions
	
	def access_instruction(self, IR, title="AccessInstruction"):
		return access_instruction(self.all_infos, self.all_commands, IR, self.debug, title=title)
	
	def retrieve_instruction(self, info):
		return retrieve_instruction(info, self.all_results, self.debug)

	def access_register(self, IR, DR, length=32, title="AccessRegister"):
		return access_register(self.all_infos, self.all_commands, IR, DR, length, self.debug, title=title)
	
	def retrieve_register(self, info):
		return retrieve_register(info, self.all_results, self.debug)
	
	def access_long_register(self, IR, DR, length, title="AccessLongRegister"):
		return access_long_register(self.all_infos, self.all_commands, IR, DR, length, self.debug, title=title)
	
	def retrieve_long_register(self, info):
		return retrieve_long_register(info, self.all_results, self.debug)
	
	def Retrieve(self, info):
		return retrieve(info, self.all_results, self.debug)

	def ResetAMchip(self):
		return ResetAMchip(self.all_commands, self.debug, title="ResetAMchip")

	def GetIDCODE(self):	
		return GetIDCODE(self.all_infos, self.all_commands)
		
	def SetChipSetup(self, ChipSetup):	
		return SetChipSetup(self.all_infos, self.all_commands, ChipSetup)

	def GetChipSetup(self):	
		return GetChipSetup(self.all_infos, self.all_commands)

	def InitEvent(self):
		return InitEvent(self.all_infos, self.all_commands)

	def SetPatternAddress(self, address):
		return SetPatternAddress(self.all_infos, self.all_commands, address)

	def GetPatternAddress(self):
		return GetPatternAddress(self.all_infos, self.all_commands)

	def WriteAndIncreasePatternAddress(self):
		return WriteAndIncreasePatternAddress(self.all_infos, self.all_commands)

	def AccessRecAddress(self):
		return AccessRecAddress(self.all_infos, self.all_commands)

	def PrepareNextRecAddress(self):
		return PrepareNextRecAddress(self.all_infos, self.all_commands)

	def SetIdleConfig(self, config):
		return SetIdleConfig(self.all_infos, self.all_commands, config)

	def PrintRecAddress(self, info):
		PrintRecAddress(info, self.all_results)

	def SaveRecAddress(self, f, info):
		SaveRecAddress(f, info, self.all_results)

	def PutDataOnBus(self, data, disabled):
		return PutDataOnBus(self.all_infos, self.all_commands, data, disabled)

	def ReadDataFromBus(self):
		return ReadDataFromBus(self.all_infos, self.all_commands)

# JTAG setup

bufSizeJTAG = 32700
defaultVerbosityJTAG = 0 # 0 - no output, 1 - general info, 2 - debug

JTAGInstance = 0

def GetJTAG(verbosity = -1):
	global JTAGInstance
	if JTAGInstance == 0:
		JTAGInstance = JTAG(bufSizeJTAG, defaultVerbosityJTAG)
	if verbosity >=0:
		JTAGInstance.SetVerbosity(verbosity)
	else:
		JTAGInstance.SetVerbosity(defaultVerbosityJTAG)
	return JTAGInstance
