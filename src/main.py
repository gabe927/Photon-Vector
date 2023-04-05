import sys
import xml.etree.ElementTree as ET

tree = ET.parse('data.xml')
root = tree.getroot()

insts = {}
instID = 0
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

    def getLoad(self):
        totalLoad = 0
        for i in self.circuits.values():
            if i != None:
                totalLoad += i.getLoad()
        return totalLoad

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

def getPhaseLoads() -> dict:
    phases = {
        "x":0,
        "y":0,
        "z":0
    }

    for mk, m in mults.items():
        for k, v in m.circuits.items():
            if v != None:
                if k == 1 or k == 4:
                    phases["x"] += v.getLoad()
                elif k == 2 or k == 5:
                    phases["y"] += v.getLoad()
                elif k == 3 or k == 6:
                    phases["z"] += v.getLoad()
    
    return phases

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

    if m is None or cirNum is None or cirNum <= 0 or cirNum >= 7:
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
    print(prefix + "Load: " + str(c.getLoad()) + "W")
    for i in c.lightInsts:
        print(prefix + "|   " + i.UID)

def dumpMult(m: mult, prefix="") -> None:
    print(prefix + "Mult: " + m.name)
    print(prefix + "Load: " + str(m.getLoad()) + "W")
    for k, v in m.circuits.items():
        if v != None:
            dumpCircuit(v, prefix=prefix + "|   ")

def dump(prefix="") -> None:
    print("---Mult/Circuit Dump---")
    for k, v in mults.items():
        dumpMult(v, prefix=prefix)


### Load Calc Functions ###

def getAvailCirInMult(m: mult) -> list:
    l = []
    for k, v in m.circuits.items():
        if v == None:
            l.append(k)
    return l

def runLoadCalc():
    print("Starting Load Calc. Loads per phase:")
    print(getPhaseLoads())
    phases = {
        "x":0,
        "y":0,
        "z":0
    }
    # put all circuits into dict | remove from mult class, but keep mult parent in circuit
    circuits = {}
    for m in mults.values():
        for cNum in m.circuits:
            c = m.circuits[cNum]
            if c != None:
                circuits.update({c:c.getLoad()})
                m.circuits[cNum] = None

    # sort list based on load
    circuits = dict(sorted(circuits.items(), key=lambda item: item[1]))
    
    # get largest loaded circuit
    for c, l in reversed(circuits.items()):
        # get available circuits from mult
        m = c.parent
        availCirsInMult = getAvailCirInMult(m)

        # get available phases from circuits
        availPhases = {}
        for i in availCirsInMult:
            if i == 1 or i == 4:
                availPhases.update({"x":phases["x"]})
            elif i == 2 or i == 5:
                availPhases.update({"y":phases["y"]})
            elif i == 3 or i == 6:
                availPhases.update({"z":phases["z"]})

        # get smallest loded availabe phase
        availPhases = dict(sorted(availPhases.items(), key=lambda item: item[1]))
        # print("available phases:")
        # print(availPhases)

        # assign circuit to mult, add load to phase
        selPhase = list(availPhases.keys())[0]
        phases[selPhase] += l
        selCircuit = None
        if selPhase == "x":
            if m.circuits[1] == None:
                selCircuit = 1
            else:
                selCircuit = 4
        elif selPhase == "y":
            if m.circuits[2] == None:
                selCircuit = 2
            else:
                selCircuit = 5
        elif selPhase == "z":
            if m.circuits[3] == None:
                selCircuit = 3
            else:
                selCircuit = 6
        c.number = selCircuit
        m.circuits[selCircuit] = c

        # print("phase loads")
        # print(phases)
    
    print("Load Calc Done. Loads per phase:")
    print(phases)
    print("Total load:")
    print(sum(phases.values()))

def getUsedInsts() -> list:
    ls = []
    for mk, m in mults.items():
        for ck, c in m.circuits.items():
            if c != None:
                for l in c.lightInsts:
                    ls.append(l)
    return ls


def exportLightInsts():
    inventory = ET.SubElement(root, "Inventory")
    invAppStamp = ET.SubElement(inventory, "AppStamp")
    invAppStamp.text = "Lightwright"

    instData = root.find("InstrumentData")

    # change AppStamp to LightWright
    instData.find("AppStamp").text = "LightWright"

    ls = getUsedInsts()    
    
    # build lighting instruments
    for l in ls:
        mainElement = ET.SubElement(instData, "UID_" + l.UID.replace('.', '_'))
        action = ET.SubElement(mainElement, "Action")
        action.text = "Update"
        timeStamp = ET.SubElement(mainElement, "TimeStamp")
        timeStamp.text = "" # TODO format the time stamp
        appStamp = ET.SubElement(mainElement, "AppStamp")
        appStamp.text = "AppStamp"
        uid = ET.SubElement(mainElement, "UID")
        uid.text = l.UID
        lwid = ET.SubElement(mainElement, "Lightwright_ID")
        lwid.text = str(l.LWID)
        cirNum = ET.SubElement(mainElement, "Circuit_Number")
        cirNum.text = str(l.circuit.number)
    
    ET.indent(tree, "  ")
    tree.write("dataOut.xml")
        

instData = root.find("InstrumentData")

instData.remove(instData.find("Action"))

univData = root.find("UniverseSettings")
root.remove(univData)

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
            li.LWID = instID
            instID += 1
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

runLoadCalc()

exportLightInsts()

dump()