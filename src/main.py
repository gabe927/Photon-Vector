import xml.etree.ElementTree as ET

tree = ET.parse('src/data.xml')
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


### Processing Funcitons ###

# gets the mult class base on mult name, creates a new one if doesn't exist
def getMultClass(name: str) -> mult:
    if name is None or name == "":
        return None

    if name not in mults:
        m = mult()
        m.name = name
        mults.update({name:m})
        return m
    else:
        return mults[name]

# gets the circuit class based on mult class and the circuit number, creates a new one if doesn't exist
def getCircuitClass(m: mult, cirNum: int) -> circuit:
    if type(cirNum) is str:
        cirNum = int(cirNum)

    if m is None or cirNum <= 0 or cirNum >= 7:
        return None

    c = m.circuits[cirNum]
    if c == None:
        c = circuit()
        c.number = cirNum
        c.parent = m
        m.circuits[cirNum] = c
    return c

def addLiToCircuit(li: lightInst, c: circuit) -> None:
    li.circuit = c
    if type(c) is circuit:
        c.lightInsts.append(li)

def convert_wattage_to_int(wattage_str):
    """
    Converts wattage in the form of a string to an integer.
    Example input: "1700W", "300 W", "1.7kW", "2.3 kW", "500", "", None
    Example output: 1700, 300, 1700, 2300, 500, 0, 0
    """
    if wattage_str is None or wattage_str == "":
        return 0
    
    wattage_str = wattage_str.strip().lower()
    wattage_int = None
    if wattage_str.isdigit():
        wattage_int = int(wattage_str)
    elif wattage_str.endswith('w'):
        wattage_int = int(wattage_str[:-1].strip())
    elif wattage_str.endswith('kw'):
        wattage_int = int(float(wattage_str[:-2].strip()) * 1000)
    return wattage_int


### Dump Functions ###

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


def runLoadCalc():
    phases = {
        "x":0,
        "y":0,
        "z":0
    }
    # put all circuits into list | remove from mult class, but keep mult parent in circuit
    # sort list based on load
    # get largest loaded circuit
    # get available phases from mult
    # get smallest loded availabe phase
    # assign circuit to mult, add load to phase

instData = root[1]
for i in reversed(instData):
    if i.tag[:3] == "UID":
        UID = None
        AppStamp = None
        CircuitName = None
        CircuitNum = None
        Wattage = None

        for j in i:
            if j.tag == "UID":
                UID = j.text
            elif j.tag == "AppStamp":
                AppStamp = j.text
            elif j.tag == "Circuit_Name":
                CircuitName = j.text
            elif j.tag == "Circuit_Number":
                CircuitNum = j.text
            elif j.tag == "Wattage":
                Wattage = j.text

        if AppStamp == "Vectorworks":
            li = lightInst()
            li.UID = UID
            li.load = convert_wattage_to_int(Wattage)
            li.mult = getMultClass(CircuitName)
            addLiToCircuit(li, getCircuitClass(li.mult, CircuitNum))
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