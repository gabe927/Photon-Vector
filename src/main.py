import xml.etree.ElementTree as ET

tree = ET.parse('data.xml')
root = tree.getroot()

insts = {}
class lightInst():
    def __init__(self) -> None:
        self.UID = ""
        self.LWID = ""
        self.deviceType = ""
        self.symbolName = ""
        self.instType = ""
        self.unitNumber = None
        self.load = 0
        self.mult = None
        self.circuit = None

mults = {}
class mult():
    def __init__(self) -> None:
        self.name = ""
        self.circuits = {
            1 : None,
            2 : None,
            3 : None,
            4 : None,
            5 : None,
            6 : None
        }
        self.unnumberedLIs = []

class circuit():
    def __init__(self) -> None:
        self.number = -1
        self.parent = None
        self.lightInsts = []
    
    def getLoad(self):
        totalLoad = 0
        for i in self.lightInsts:
            totalLoad += i.load
        return totalLoad

# gets the mult class base on mult name, creates a new one if doesn't exist
def getMultClass(name: str) -> mult:
    if j.text not in mults:
        m = mult()
        m.name = j.text
        mults.update({j.text:m})
        return m
    else:
        return mults[j.text]

# gets the circuit class based on mult class and the circuit number, creates a new one if doesn't exist
def getCircuitClass(m: mult, cirNum: int) -> circuit:
    c = m.circuits[cirNum]
    if c == None:
        c = circuit()
        c.number = cirNum
        c.parent = m
        m.circuits[cirNum] = c
    return c

def addLiToCircuit(li: lightInst, c: circuit) -> None:
    li.circuit = c
    c.lightInsts.append(li)

def dumpCircuit(c: circuit, prefix=""):
    print(prefix + "Circuit " + str(c.number))
    for i in c.lightInsts:
        print(prefix + "|   " + i.UID)

def dumpMult(m: mult, prefix="") -> None:
    print(prefix + "Mult: " + m.name)
    for k, v in m.circuits.items():
        if v != None:
            dumpCircuit(v, prefix=prefix + "|   ")

def dump(prefix="") -> None:
    print("---Mult/Circuit Dump---")
    for k, v in mults.items():
        dumpMult(v, prefix=prefix)

instData = root[1]
for i in reversed(instData):
    if i.tag[:3] == "UID":
        li = lightInst()
        for j in i:
            if j.tag == "UID":
                li.UID = j.text
            elif j.tag == "Circuit_Name" and j.text != None:
                li.mult = getMultClass(j.text)
            elif j.tag == "Circuit_Number" and j.text != None:
                cirNum = int(j.text)
                if li.mult == None:
                    continue
                c = getCircuitClass(li.mult, cirNum)
                addLiToCircuit(li, c)

        insts.update({li.UID:li})
        instData.remove(i)

print(insts)
print("****____****____****____****")
print(mults)
# Key sort
mults = dict(sorted(mults.items()))
# Value sort
# mults = dict(sorted(mults(), key=lambda item: item[1]))
print(mults)
print("****____****____****____****")
for i in instData:
    print(i.tag)

dump()