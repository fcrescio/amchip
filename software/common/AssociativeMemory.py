class AssociativeMemory:

    def __init__(self, size):
        self.npatt = size
        self.patterns = [ 0 for x in range(size) ]
        self.sslayers = [ {} for x in range(8) ]
        self.addr = 0
    
    def dontcareDecode(self, data, ndc):
        head = data>>(ndc*2)
        result = [head<<ndc]
        for bit in range(ndc):
            code = (data>>(bit*2))&0x3
            if code == 0x1:
                result = [ x|(0<<bit) for x in result ]
            elif code == 0x2:
                result = [ x|(1<<bit) for x in result ]
            elif code == 0x0:
		result = [ item for sublist in [ [ x|(0<<bit), x|(1<<bit) ] for x in result ] for item in sublist ] 
            else:
                return []
        return result

    def writePattern(self, address, pattern, ndc=[0,0,0,0,0,0,0,0]):
        
        if type(pattern) is list:
            if len(pattern) == 8:
                for i in range(8):
                    for data in self.dontcareDecode(pattern[i],ndc[i]):
                        if data in self.sslayers[i]:
                            self.sslayers[i][data].append(address)
                        else:
                            self.sslayers[i][data] = [address]
            else:
                print("Pattern size is not 8!")
        else:
            print("Pattern is not a list!")

    def writePatternIncr(self, pattern,  ndc=[0,0,0,0,0,0,0,0]):
        self.writePattern(self.addr, pattern, ndc)
        self.addr+=1

    def setAddress(self,addr):
        self.addr = addr

    def sendData(self, bus, data):
        if data in self.sslayers[bus]:
            matches = self.sslayers[bus][data]
        else:
            matches = []
        for match in matches:
            self.patterns[match] |= (1<<bus)

    def getFoundPatterns(self, thr):
        found = [i for i, x in enumerate(self.patterns) if bin(x).count("1") >= thr]
        return found

    def getHitmap(self, patt):
        return self.patterns[patt]

    def initBank(self):
        self.patterns = [0 for x in range(self.npatt)]

    def getPatternWord(self,patt):
        return "%.8x"%(patt+(self.getHitmap(patt)<<24))

    def getPattern(self,patt):
	return patt+(self.getHitmap(patt)<<24)
