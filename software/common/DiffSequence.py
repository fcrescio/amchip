class DiffSequence:
    def __init__(self,listA = [], listB = []):
        self.listA = listA
        self.listB = listB
        self.aligned = {}

    def align(self):
        aligned = {}
	nextA = 0
        for idxA, elemA in enumerate(self.listA):
            startB = 0
	    if idxA < nextA:
		continue
            while startB < len(self.listB):
                try:
                    idxB = self.listB[startB:].index(elemA)
                    offset = startB
                    count = 0
                    myidxA = idxA
                    myidxB = idxB
                    while (myidxA < len(self.listA)) and (myidxB+offset < len(self.listB)) and (self.listA[myidxA] == self.listB[myidxB+offset]) :
                        count += 1
                        myidxA += 1
                        myidxB += 1
                    aligned[count] = [idxA,idxB]
		    if startB == 0:
			nextA = myidxA
                    startB += idxB + 1
                except ValueError:
                    startB = len(self.listB)
        self.aligned = aligned
        return aligned

    def maxAlign(self):
        return sorted(self.aligned.keys(),reverse=True)[0]

    def loopMatch(self,startB):
        match = 0
        error = 0
        idxB = 0
        lenB = len(self.listB)
        for idxA, elemA in enumerate(self.listA):
            if self.listA[idxA] == self.listB[(idxB+startB)%lenB]:
            	print("%d %.8x = %.8x"%(idxA,self.listA[idxA], self.listB[(idxB+startB)%lenB]))
                match += 1
            else:
            	print("%d %.8x = %.8x ***"%(idxA,self.listA[idxA], self.listB[(idxB+startB)%lenB]))
                error += 1
            idxB += 1

        return match, error
