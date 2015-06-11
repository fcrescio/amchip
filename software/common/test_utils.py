from random import *
from utils import * 
from JTAG import * 
from ADC import * 
import AssociativeMemory
import DiffSequence
import difflib

SizeOfChip = 3072

def expand_dcbits(data, dcbits):
	expanded = 0
	for i in xrange(18-dcbits):
		if i < dcbits:
			expanded |= (1<<(i*2)) if (data>>i)&(0x1) == 0 else (2<<(i*2))
		else: 
			expanded |= ((data>>i)&0x1)<<(i+dcbits)
	return expanded

def ReadADC(userCTRL="no", userCONFIG="no"):
	a = GetADC()
	return a.ReadVal(userCTRL, userCONFIG)

def JustReadADC():
	a = GetADC()
	return a.JustReadVal()

def ReadIDCODE():
	j = GetJTAG(verbosity=2)
	j.ResetAMchip()
	id_code = j.GetIDCODE()
	j.Dispatch()
	return j.Retrieve(id_code)

def ClearPatternBank():
	print("Clear pattern bank")
	silent = True

	t = Tick()
	j = GetJTAG()

	j.ResetAMchip()
	j.GetIDCODE()

	# imposto TMODE = 1 e scrivo una banca di pattern tutta abilitata
	ChipSetup = jpatt_ctrl_gen(tmode=0x1)
	j.SetChipSetup(ChipSetup)
	j.InitEvent()

	j.SetPatternAddress(0x0)
	j.PutDataOnBus(data=[0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5], disabled=True)
	for i in range(SizeOfChip):
		j.WriteAndIncreasePatternAddress()
	j.GetPatternAddress()
	j.PutDataOnBus(data=[0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0], disabled=False)
	ChipSetup = jpatt_ctrl_gen(tmode=0x0,disabled=0x2,thr=0xf)
	j.SetChipSetup(ChipSetup)
	j.InitEvent()
	j.InitEvent()
	j.Dispatch()
	if not silent:
		j.PrintResults()
		Tock(t, "Clear pattern bank")

def GenBank(size): 
	print("Gen bank")
	bank = [ [randint(0, 0xFFff) for x in range(8)] for y in range(size) ]

	return bank

def GenIncrementalBank(size):
	print("Gen bank")
	bank = [ [y for x in range(8) ] for y in range(size) ]
	return bank

def LoadBank(bank, offset):
	if offset + len(bank) > SizeOfChip:
		print Error_("LoadBank:: Chip can contain %d patterns only"%(SizeOfChip))
		raise

	bank_size = len(bank)

	print("Configure AMchip")

	j = GetJTAG(verbosity=1)
	j.ResetAMchip()
	ChipSetup = jpatt_ctrl_gen(tmode=0x1, disabled=0x0, dcbits = 0x22222222,thr=0xf)
	j.SetChipSetup(ChipSetup)
	j.InitEvent()

	print "Delete bank"
	j.SetPatternAddress(0x0)
	j.PutDataOnBus(data=[randint(1, 0xffff) for x in range(8)] , disabled=True)
	for i in range(SizeOfChip):
		j.WriteAndIncreasePatternAddress()

	print "Write bank"
	ChipSetup = jpatt_ctrl_gen(tmode=0x1, disabled=0x0, dcbits = 0x22222222,thr=0xf)
	j.SetPatternAddress(offset)
	for (i, pattern) in enumerate(bank):
		swapPattern = [pattern[0], pattern[1], pattern[2], pattern[3],pattern[4], pattern[5], pattern[6], pattern[7]]
		data = [expand_dcbits(x,2) for x in swapPattern]
		j.PutDataOnBus(data, disabled=False)
		j.WriteAndIncreasePatternAddress()

	j.PutDataOnBus(data=[0 for x in range(8)] , disabled=True)
	ChipSetup = jpatt_ctrl_gen(tmode=0x0, disabled=0x0, dcbits = 0x22222222,thr=0xf, strength=0x0)
	j.SetChipSetup(ChipSetup)
	j.InitEvent()
	j.InitEvent()
	j.Dispatch()

def GenIncrementalData(size, bank):
	print("Gen data")
	data = [ [ ((y*2 % (len(bank)))<<16)|((y*2+1)%(len(bank))) for x in range(8) ] for y in range(size) ]
	return data

def GenData(size, bank, injectFactor):
	print("Gen data")
	data = [ [randint(1,0xffffffff) for x in range(8)] for y in range(size) ]

	print("Randomly inject bank data in the stream")
	for i in range(injectFactor):
		patt = randint(0,len(bank)-1)
		for bus in range(8):
			data[randint(0, size-1)][bus] = (data[randint(0, size-1)][bus] & 0xFFFF0000) | bank[patt][bus]

	return data

def GenDataFromBank(size, bank, injectFactor):
	print("Gen data")
	randomPatt = [randint(0,len(bank)-1) for y in range(size*2)]
	data = [ [(bank[randomPatt[y*2]][x]<<16)|(bank[randomPatt[y*2+1]][x]) for x in range(8)] for y in range(size) ]
        print("Randomly inject random data in the stream")
        for i in range(injectFactor):
                for bus in range(8):
                        data[randint(0, size-1)][bus] = randint(0,0xffffffff)

	return data

def PredictStream(bank, offset, data, eventSize, threshold):
	print("Compute expected patterns sequence")
	myam = AssociativeMemory.AssociativeMemory(len(bank))

	for pattern in bank:
		myam.writePatternIncr(pattern)

	lcm=eventSize
	while(lcm%len(data)):
		lcm+=eventSize
	print("%d different events"%(lcm/eventSize))
	expectlist = []
	eventlist = []
	idx = 0
	for events in range(lcm/eventSize):
		# print "%.8d\r"%(events),
		for cycles in range(eventSize):
			for bus in range(8):
				myam.sendData(bus,data[idx][bus]&0xFFFF)
				myam.sendData(bus,(data[idx][bus]>>16)&0xFFFF)
			idx = (idx + 1)%len(data)
		found = myam.getFoundPatterns(threshold)
		patterns = [patt+offset+(myam.getHitmap(patt)<<24) for patt in found]
		eventlist.append(patterns)
		for patt in found:
			expectlist.append(myam.getPattern(patt)+offset)
		myam.initBank()

	listlen = len(expectlist)
	testedpatt = len(set([x&0xfff for x in expectlist]))
	print("The sequence is %d patterns long with %d different patterns for a %f coverage of the bank."%(listlen,testedpatt,testedpatt/float(len(bank))))
	return [expectlist, eventlist]

def StopGTX():
	print "Stop sending data"
	WriteREG("PATTOUT.CTRL.FREEZE", 1)
	WriteREG("GTX.CTRL.ENABLED", 0)

	
# same size event result
def WriteFullRateSameLengthProgram(expectedEvents,eventSize):
	myIdleWait = 16
	eventaddr = 0
	instr = []
	instr.append(iIDLE | myIdleWait)
	maxwait = 0
	for event in expectedEvents:
		maxwait = max(maxwait, max(0,eventSize-len(event)))
	print("maxwait %d"%(maxwait))
	for chunk in range(eventSize//(2**9)):
		instr.append(iDATA | (2**9)-1)
	if(eventSize%(2**9)>0):
		instr.append(iDATA | (eventSize%(2**9))-1)
	instr.append(iIDLE | (maxwait+myIdleWait))
	instr.append(iOPCODE | opcode_init)
	instr.append(iIDLE | myIdleWait)
	instr.append(iGOTO | len(expectedEvents))
	instr.append(iADDR | 1)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | len(instr)-1)
	print "Write program"
	print ["%x"%(x) for x in instr]
	WriteREG("GTX.CTRL.RESET_CONTROLLERS", 1)
	Clear("GTX.HIT_INSTR")
	Upload("GTX.HIT_INSTR", instr)

	instr = []
	instr.append(iIDLE | 10)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)

	Clear("GTX.PATTIN0_INSTR")
	Clear("GTX.PATTIN1_INSTR")
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)

def WriteFullRateProgram(expectedEvents,eventSize):
	myIdleWait = 16
	eventaddr = 0
	instr = []
	instr.append(iIDLE | myIdleWait)
	for event in expectedEvents:
		for chunk in range(eventSize//(2**9)):
			instr.append(iDATA | (2**9)-1)
		if(eventSize%(2**9)>0):
			instr.append(iDATA | (eventSize%(2**9))-1)
		instr.append(iIDLE | (max(0,len(event)-eventSize))+myIdleWait)
		instr.append(iALLIGN_PREDICTED | eventaddr)
		eventaddr += len(event)
		instr.append(iOPCODE | opcode_init)
		instr.append(iIDLE | myIdleWait)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)
	print ["%x"%(x) for x in instr]
	print "Write program"
	WriteREG("GTX.CTRL.RESET_CONTROLLERS", 1)
	Clear("GTX.HIT_INSTR")
	Upload("GTX.HIT_INSTR", instr)

	instr = []
	instr.append(iIDLE | 10)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)

	Clear("GTX.PATTIN0_INSTR")
	Clear("GTX.PATTIN1_INSTR")
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)


# eventSize must be a power of 2
def PrepareEventInstructions(eventSize, allignAddress, insertIdles = 0):
	chunk = 2**9
	smallLoop = eventSize//chunk

	instr = []
	instr.append(iIDLE | 10) # relativeAddr + 0

	for i in xrange(smallLoop):
		instr.append(iDATA | (chunk-1))
		if insertIdles>0:
			instr.append(iIDLE | (chunk*insertIdles-1) )

	instr.append(iIDLE | 10)
	instr.append(iALLIGN_PREDICTED | allignAddress)
	instr.append(iIDLE | 10)
	instr.append(iOPCODE | opcode_init)
	instr.append(iIDLE | 10)
	return instr

def WriteHitSendProgram(rate):
	print "Write program"
	WriteREG("GTX.CTRL.RESET_CONTROLLERS", 1)
	instr = []
	instr.append(iDATA | rate)
	instr.append(iIDLE | (100-rate))
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)

	Clear("GTX.HIT_INSTR")
	Upload("GTX.HIT_INSTR", instr)

	instr = []
	instr.append(iIDLE | 10)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)

	Clear("GTX.PATTIN0_INSTR")
	Clear("GTX.PATTIN1_INSTR")
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)
# eventSize must be greater than 500 if you want proper ADC sampling
def WritePrograms(expectedEvents, eventSize, sampleADC = True):
	print "Write program"
	WriteREG("GTX.CTRL.RESET_CONTROLLERS", 1)
	NofDataRates = 8
	RepeatDataRate = 4

	instr = []
	instr.append(iIDLE | 10)

	for rate in xrange(NofDataRates):
		gotoAddr = len(instr)

		allignAddress = 0
		for i in xrange(len(expectedEvents)):
			instr.extend(PrepareEventInstructions(eventSize, allignAddress, insertIdles = rate))
			if sampleADC:
				instr.append(iSAMPLE_ADC)
			allignAddress = allignAddress + len(expectedEvents[i])

		instr.append(iGOTO | RepeatDataRate)
		instr.append(iADDR | gotoAddr)

	instr.append(iIDLE)
	instr.append(iIDLE)
	instr.append(iIDLE)
	#instr.append(iGOTO | iINFINITE)
	#instr.append(iADDR | 0)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | gotoAddr)

	# for i in xrange(len(instr)):
	# 	print hex(i), hex(instr[i])

	Clear("GTX.HIT_INSTR")
	Upload("GTX.HIT_INSTR", instr)

	instr = []
	instr.append(iIDLE | 10)
	instr.append(iGOTO | iINFINITE)
	instr.append(iADDR | 0)

	Clear("GTX.PATTIN0_INSTR")
	Clear("GTX.PATTIN1_INSTR")
	Upload("GTX.PATTIN0_INSTR", instr)
	Upload("GTX.PATTIN1_INSTR", instr)

def LoadHits(data):
	print "Fill BUS RAM"
	
	for l in range(8):
		busdata = []
		for hits in data:
			busdata.append(hits[l])
		Upload("GTX.HIT"+str(l), busdata)

def LoadPredictedPatterns(patterns):
	print("Load Predicted Patterns")
	
	debug = False
	ReadREG("PATTOUT.CTRL", debug)
	WriteREG("PATTOUT.CTRL",0xB7, debug, title="ResetErrorsCounterAndAddresses")
	Clear("PATTOUT.PREDICTED_PATTERNS")
	Clear("PATTOUT.PATTOUT")
	Clear("PATTOUT.EXPECTED")
	Clear("PATTOUT.RECEIVED")
	Clear("PATTOUT.EXTRA")
	# patterns[5] = 0
	WriteREG("PATTOUT.STREAM_MAX_ADDR", len(patterns)-1, debug, title="WriteStreamMaxAddr")
	WriteREG("PATTOUT.MAX_ERR_PER_EVENT", 10, debug, title="WriteMaxErrorsPerEvent")
	Upload("PATTOUT.PREDICTED_PATTERNS", patterns)

def StartGTX(threshold):
	print("Configure AMchip")

	j = GetJTAG()
	j.ResetAMchip()
	j.SetIdleConfig(0x0100007f)
	ChipSetup = jpatt_ctrl_gen(tmode=0x0, disabled=0x2, dcbits = 0x22222222,thr=threshold,strength=0x0)
	j.SetChipSetup(ChipSetup)
	j.InitEvent()
	j.InitEvent()
	j.Dispatch()

	print "Start sending data"

	# spy_size = 2**15
	# Clear("SPY.SPY")
	# Clear("SPY.SPY_EXTRA")
	# WriteREG("SPY.HOLD_ADDR", spy_size/2)
	# WriteREG("SPY.CTRL", 0x7 | (0x0<<4))

	WriteREG("PATTOUT.CTRL.RESET_ADDRESSES", 1)
	WriteREG("PATTOUT.CTRL.FREEZE", 0)
	WriteREG("GTX.CTRL.ENABLED", 1)
	WriteREG("PATTOUT.CTRL.RESET_COUNTER", 1)

def DumpPattoutEvents():
	debug = False
	ReadREG("PATTOUT.STATUS", debug, title="PATTOUT.STATUS")
	CTRL = ReadREG("PATTOUT.CTRL", debug)
	WriteREG("PATTOUT.CTRL", CTRL | 0x1, debug, title="Freeze")
	pattout = Dump("PATTOUT.PATTOUT")
	extra = Dump("PATTOUT.EXTRA")
	overflowed = ReadREG("PATTOUT.STATUS", debug) & 0x1
	freeze_addr = ReadREG("PATTOUT.PATTOUT_FREEZE_ADDR", debug=False)
	WriteREG("PATTOUT.CTRL", CTRL & 0xFE, debug, title="UnFreeze")

	#print "overflowed", overflowed, "freeze_addr",  freeze_addr
	#for i in xrange(len(pattout)):
	#	print i, "pout %x  extra %x"%(pattout[i], extra[i])

	if overflowed>0 and freeze_addr != 0:
		freeze_addr = freeze_addr - 1
		new_pattout = []
		new_extra = []
		# print len(pattout[freeze_addr+1:len(pattout)]), len(pattout[0:freeze_addr+1])

		new_pattout.extend(pattout[freeze_addr+1:len(pattout)])
		new_pattout.extend(pattout[0:freeze_addr+1])

		new_extra.extend(extra[freeze_addr+1:len(extra)])
		new_extra.extend(extra[0:freeze_addr+1])
	else:
		new_pattout = pattout
		new_extra = extra

	print "new_pout len = %d pout len = %d"%(len(new_pattout), len(pattout))
	for i in xrange(len(new_pattout)):
		print i, "pout %x  extra %x"%(new_pattout[i], new_extra[i])

	idx = 0
	events = [ [] ]
	for i, pattern in enumerate(new_pattout):
		if (new_extra[i] & 0x1) == 1:
			idx += 1
			events.append([])
			continue
		events[idx].append(pattern)

	if len(events)>0:
		del events[0]
	if len(events)>0:
		del events[-1]

	pmax = max([len(event) for event in events])
	pmin = min([len(event) for event in events])
	# if pmin != pmax:
	# 	for i in xrange(len(pattout)):
	# 		print i, "new_pout %x  pout %x"%(new_pattout[i], pattout[i])
	print("%d full events"%(len(events)))
	print("%d patterns in longest event"%(pmax))
	print("%d patterns in smallest event"%(pmin))
	print("%f patterns in average"%(sum([len(event) for event in events])/float(len(events))))

	return events

def CompareEvents(eventlist, expectlist, silent = False):
	missing = []
	extra = []
	wrongHitmap = []

	for event_idx,event in enumerate(eventlist):
		if len(event)>0:
			firstNonEmpty = event_idx
			break

	alignfirstevent = [difflib.SequenceMatcher(None,eventlist[0],expected).ratio() for expected in expectlist]
	# print alignfirstevent
	expected_idx = alignfirstevent.index(max(alignfirstevent))

	for event_idx,event in enumerate(eventlist):
		#if event_idx >= len(expectlist) or expected_idx >= len(expectlist):
		#	continue
		if len(event)==0 and len(expectlist[expected_idx])==0:
			expected_idx += 1
			continue
		if len(event)==0:
			print("Event %d is empty!"%(event_idx))
			continue
		if len(expectlist[expected_idx])==0:
			print("Expected empty event at position %d - %d"%(event_idx,expected_idx))
			print(["%.8x"%(x) for x in event])
			expected_idx += 1
			continue
		if difflib.SequenceMatcher(None,event, expectlist[expected_idx]).ratio() == 1:
			print("Event %d is aligned with %d"%(event_idx,expected_idx))
		else:
			print("Event %s is not perfectly aligned with %d"%(event_idx,expected_idx))
			idx_a = 0
			idx_b = 0
			for i in range(max([len(event),len(expectlist[expected_idx])])):
				if (idx_a == len(event)) or (idx_b == len(expectlist[expected_idx])):
					break
				if event[idx_a] == expectlist[expected_idx][idx_b]:
					idx_a += 1
					idx_b += 1
				else:
					if event[idx_a]&0xfffff > expectlist[expected_idx][idx_b]&0xfffff:
						if not silent:
							print("Event %d pattern %.8x is missing"%(event_idx,expectlist[expected_idx][idx_b]))
						missing.append(expectlist[expected_idx][idx_b])
						idx_b += 1
					elif event[idx_a]&0xfffff < expectlist[expected_idx][idx_b]&0xfffff:
						if not silent:
							print("Event %d extra pattern %.8x"%(event_idx,event[idx_a]))
						extra.append(event[idx_a])
						idx_a += 1
					else:
						if not silent:
							print("Event %d wrong hitmap %.8x expected %.8x [%.8x]"%(event_idx,event[idx_a],expectlist[expected_idx][idx_b],event[idx_a] ^ expectlist[expected_idx][idx_b]))
						diffbitmap = (event[idx_a]>>24) ^ (expectlist[expected_idx][idx_b]>>24)
						extrabitmap = diffbitmap & (event[idx_a]>>24)
						missbitmap = diffbitmap & (expectlist[expected_idx][idx_b]>>24)
						wrongHitmap.append({"expected" : expectlist[expected_idx][idx_b], "received" : event[idx_a]})
						# if event[idx_a]&0xfffff in result:
						# 	result[event[idx_a]&0xfffff].append([extrabitmap,missbitmap])
						# else:
						# 	result[event[idx_a]&0xfffff] = [[extrabitmap,missbitmap]]
						idx_a += 1
						idx_b += 1
							
		expected_idx = (expected_idx + 1)%len(expectlist)
		while len(expectlist[expected_idx]) == 0:
			expected_idx = (expected_idx + 1)%len(expectlist)

	return {"missing" : missing, "extra" : extra, "wrongHitmap" : wrongHitmap}

def ReadErrorRate(silent):
	errorsTotal0 = ReadREG("PATTOUT.N_of_ERRORS", debug=False, title="ReadErrorsTotal")
	t = Tick()
	sleep(1)
	errorsTotal1 = ReadREG("PATTOUT.N_of_ERRORS", debug=False, title="ReadErrorsTotal")
	time_passeed = Tock(t)
	errorRate = (errorsTotal1 - errorsTotal0)/time_passeed
	outputString = "Errors Rate: %f Time: %f seconds. ErrorsTotal: %d"%(errorRate, time_passeed, errorsTotal1)
	if not silent:
		print outputString
	return [errorRate, time_passeed, errorsTotal1, outputString]
